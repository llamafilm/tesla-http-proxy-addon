import os
import logging
import requests

SUPERVISOR_TOKEN = os.environ['SUPERVISOR_TOKEN']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
DOMAIN = os.environ['DOMAIN']
REGION = os.environ['REGION']
DEBUG = os.environ['DEBUG']
SCOPES = 'openid offline_access vehicle_device_data vehicle_cmds vehicle_charging_cmds energy_device_data energy_cmds'
AUDIENCE = {
    'North America, Asia-Pacific': 'https://fleet-api.prd.na.vn.cloud.tesla.com',
    'Europe, Middle East, Africa': 'https://fleet-api.prd.eu.vn.cloud.tesla.com',
    'China'                      : 'https://fleet-api.prd.cn.vn.cloud.tesla.cn'
}[REGION]

if DEBUG == 'true':
    log_level = logging.DEBUG
else:
    log_level = logging.INFO
logging.basicConfig(format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s',
    level=log_level, datefmt='%H:%M:%S')
logger = logging.getLogger('auth')

# generate partner authentication token
logger.info('Generating Partner Authentication Token')

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
logger.info('Registering Tesla account...')
req = requests.post(f'{AUDIENCE}/api/1/partner_accounts',
    headers={
        'Authorization': 'Bearer ' + tesla_api_token,
        'Content-Type': 'application/json'
    },
    data='{"domain": "%s"}' % DOMAIN
)
if req.status_code >= 400:
    logger.error("Error %s: %s", req.status_code, req.text)
    raise SystemExit(1)
logger.debug(req.text)

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
