import os
import logging
import requests

from const import (
    SCOPES,
    AUDIENCES,
    TESLA_AUTH_ENDPOINTS,
)

SUPERVISOR_TOKEN = os.environ['SUPERVISOR_TOKEN']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
DOMAIN = os.environ['DOMAIN']
REGION = os.environ['REGION']
DEBUG = os.environ['DEBUG']
AUDIENCE = AUDIENCES[REGION]
TESLA_AUTH_ENDPOINT = TESLA_AUTH_ENDPOINTS[REGION]


if DEBUG == 'true':
    log_level = logging.DEBUG
else:
    log_level = logging.INFO
logging.basicConfig(format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s',
    level=log_level, datefmt='%H:%M:%S')
logger = logging.getLogger('auth')

# generate partner authentication token
logger.info('Generating Partner Authentication Token')

req = requests.post(f"{TESLA_AUTH_ENDPOINT}/oauth2/v3/token",
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
