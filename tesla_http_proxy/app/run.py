import os
import uuid
import requests
from flask import Flask, request, render_template
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

SUPERVISOR_TOKEN = os.environ['SUPERVISOR_TOKEN']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
DOMAIN = os.environ['DOMAIN']
SCOPES = 'openid offline_access vehicle_device_data vehicle_cmds vehicle_charging_cmds'
AUDIENCE = 'https://fleet-api.prd.na.vn.cloud.tesla.com'

# generate partner authentication token
print('\n*** Generating Partner Authentication Token *** \n')
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
payload = {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'scope': SCOPES,
    'audience': AUDIENCE
}
req = requests.post('https://auth.tesla.com/oauth2/v3/token', headers=headers, data=payload)
req.raise_for_status()
tesla_api_token = req.json()['access_token']

# register Tesla account to enable API access
print('\n*** Registering Tesla account *** \n')
req = requests.post('https://fleet-api.prd.na.vn.cloud.tesla.com/api/1/partner_accounts',
    headers={
    'Authorization': 'Bearer ' + tesla_api_token,
    'Content-Type': 'application/json'
    },
    data='{"domain": "%s"}' % DOMAIN
)
print(req.text)
req.raise_for_status()

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
    return render_template('index.html', domain=DOMAIN, client_id=CLIENT_ID,
        scopes=SCOPES, randomstate=uuid.uuid4().hex, randomnonce=uuid.uuid4().hex)

@app.route('/callback')
def callback():
    """Handle POST callback from Tesla server to complete OAuth"""

    # app.logger.warning('callback args: %s' % request.args)
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
    app.logger.warning('Refresh token for Fleet API requests: %s', req.json()['refresh_token'])
    req.raise_for_status()
    with open('/data/refresh_token', 'w') as f:
        f.write(req.json()['refresh_token'])
    with open('/data/access_token', 'w') as f:
        f.write(req.json()['access_token'])

    return render_template('callback.html')

@app.route('/shutdown')
def shutdown():
    """Shutdown Flask server so the HTTP proxy can start"""
    os._exit(0)

if __name__ == '__main__':
    print('\n*** Starting Flask server... *** \n')
    app.run(port=8099, debug=False, host='0.0.0.0')
