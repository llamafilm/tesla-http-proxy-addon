import os
import uuid
import logging
import requests
from flask import  cli, Flask, Response, request, render_template
from werkzeug.exceptions import HTTPException

logging.basicConfig(format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s',
    level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger('main')

app = Flask(__name__)

SUPERVISOR_TOKEN = os.environ['SUPERVISOR_TOKEN']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
DOMAIN = os.environ['DOMAIN']
REGION = os.environ['REGION']
SCOPES = 'openid offline_access vehicle_device_data vehicle_cmds vehicle_charging_cmds energy_device_data energy_cmds'
AUDIENCE = {
    'North America, Asia-Pacific': 'https://fleet-api.prd.na.vn.cloud.tesla.com',
    'Europe, Middle East, Africa': 'https://fleet-api.prd.eu.vn.cloud.tesla.com',
    'China'                      : 'https://fleet-api.prd.cn.vn.cloud.tesla.cn'
}[REGION]

BLUE = "\u001b[34m"
RESET = "\x1b[0m"

# generate partner authentication token
logger.info('*** Generating Partner Authentication Token ***')

req = requests.post('https://auth.tesla.com/oauth2/v3/token',
    headers={
        'Content-Type': 'application/x-www-form-urlencoded'},
    data={
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': SCOPES,
        'audience': AUDIENCE
    }
)
if req.status_code >= 400:
    logger.error("HTTP %s: %s", req.status_code, req.reason)
logger.debug(req.text)
try:
    tesla_api_token = req.json()['access_token']
except KeyError:
    logger.error("Response did not include access token: %s", req.text)
    raise SystemExit(1)

# register Tesla account to enable API access
logger.info('*** Registering Tesla account ***')
req = requests.post(f'{AUDIENCE}/api/1/partner_accounts',
    headers={
        'Authorization': 'Bearer ' + tesla_api_token,
        'Content-Type': 'application/json'
    },
    data='{"domain": "%s"}' % DOMAIN
)
if req.status_code >= 400:
    logger.error("Error %s: %s", req.status_code, req.reason)
    raise SystemExit(1)
logger.info(req.text)


@app.errorhandler(Exception)
def handle_exception(e):
    """Exception handler for HTTP requests"""

    app.logger.error(e)
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return 'Unknown Error', 500


@app.route('/')
def index():
    """Web UI for add-on inside Home Assistant"""

    slug = os.uname().nodename.replace('-', '_')
    return render_template('index.html', slug=slug, domain=DOMAIN, client_id=CLIENT_ID,
        scopes=SCOPES, randomstate=uuid.uuid4().hex, randomnonce=uuid.uuid4().hex)


@app.route('/callback')
def callback():
    """Handle POST callback from Tesla server to complete OAuth"""

    app.logger.debug('callback args: %s', request.args)
    # sometimes I don't get a valid code, not sure why
    try:
        code = request.args['code']
    except KeyError:
        app.logger.error('args: %s', request.args)
        return 'Invalid code!', 400

    # Exchange code for refresh_token
    req = requests.post('https://auth.tesla.com/oauth2/v3/token',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded'},
        data={
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'audience': AUDIENCE,
            'redirect_uri': f"https://{DOMAIN}/callback"
        }
    )

    app.logger.warning(f"Info to enter into Tesla Custom component:\n \
        Refresh token  : {BLUE}{req.json()['refresh_token']}{RESET}\n \
        Proxy URL      : {BLUE}https://{os.uname().nodename}{RESET}\n \
        SSL certificate: {BLUE}/share/tesla/selfsigned.pem{RESET}\n \
        Client ID      : {BLUE}{CLIENT_ID}\n{RESET}")

    req.raise_for_status()
    with open('/data/refresh_token', 'w') as f:
        f.write(req.json()['refresh_token'])
    with open('/data/access_token', 'w') as f:
        f.write(req.json()['access_token'])

    return render_template('callback.html')


@app.route('/shutdown')
def shutdown():
    """Restart this addon so the HTTP proxy can start"""

    response = Response('', 204)

    # disable regenerate_auth to skip Python code on next launch
    req = requests.get('http://supervisor/addons/self/options/config',
        headers={
            'Authorization': f'Bearer {SUPERVISOR_TOKEN}'
        }
    )
    options = req.json()['data']
    options['regenerate_auth'] = False

    req = requests.post('http://supervisor/addons/self/options',
        headers={
            'Authorization': f'Bearer {SUPERVISOR_TOKEN}'
        },
        json={
            'options': options
        }
    )

    @response.call_on_close
    def on_close():
        # this runs after returning the HTTP response
        req = requests.post('http://supervisor/addons/self/restart',
            headers={
                'Authorization': f'Bearer {SUPERVISOR_TOKEN}'
            })
        logger.warning(req.text) # this line should never run

    return response


if __name__ == '__main__':
    logger.info('*** Starting Flask server... ***')
    cli.show_server_banner = lambda *_: None
    app.run(port=8099, debug=False, host='0.0.0.0')
