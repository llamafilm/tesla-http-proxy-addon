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
print('\n### Generate Partner Authentication Token ###')
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
payload = {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'scope': 'openid vehicle_device_data vehicle_cmds vehicle_charging_cmds',
    'audience': AUDIENCE
}
req = requests.post('https://auth.tesla.com/oauth2/v3/token', headers=headers, data=payload)
req.raise_for_status()
tesla_api_token = req.json()['access_token']

# register Tesla account to enable API access
print('\n### Registering Tesla account ###')
headers = {
    'Authorization': 'Bearer ' + tesla_api_token,
    'Content-Type': 'application/json'
}
payload = '{"domain": "%s"}' % DOMAIN
req = requests.post('https://fleet-api.prd.na.vn.cloud.tesla.com/api/1/partner_accounts', headers=headers,data=payload)
print(req.text)
req.raise_for_status()

@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # now you're handling non-HTTP exceptions only
    return 'Unknown Error', 500

# Web UI for add-on inside Home Assistant
@app.route('/')
def index():
    return render_template('index.html', domain=DOMAIN, client_id=CLIENT_ID, scopes=SCOPES, randomstate=uuid.uuid4().hex, randomnonce=uuid.uuid4().hex)

# Tesla servers POST here to complete authorization
@app.route('/callback')
def callback():
    # sometimes I don't get a valid code, not sure why
    try:
        code = request.args['code']
    except KeyError:
        app.logger.error('args: %s' % request.args)
        return f'Invalid code!', 400

    # Exchange code for refresh_token
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'audience': AUDIENCE,
        'redirect_uri': f"https://{DOMAIN}/callback"
    }
    req = requests.post('https://auth.tesla.com/oauth2/v3/token', headers=headers, data=payload)
    app.logger.warning('Access token for Fleet API requests: %s' % req.json()['access_token'])
    app.logger.warning('Refresh token for Fleet API requests: %s' % req.json()['refresh_token'])
    req.raise_for_status()
    with open('/data/refresh_token', 'w') as f:
        f.write(req.json()['refresh_token'])
    with open('/data/access_token', 'w') as f:
        f.write(req.json()['access_token'])

    return '<html><head><meta name="viewport" content="initial-scale=1.0"></head><body><div style="text-align:center;padding:100px;"><a href="homeassistant://navigate"><button type="button">Return to Home Assistant</button></a></div></body></html>'

# Exit cleanly so the HTTP Proxy can start
@app.route('/shutdown')
def shutdown():
    os._exit(0)

if __name__ == '__main__':
    print('\n### Starting Flask server... ###')
    app.run(port=8099, debug=True, host='0.0.0.0')
