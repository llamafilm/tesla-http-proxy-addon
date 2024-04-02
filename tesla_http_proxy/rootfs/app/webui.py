import os
import logging
import random
import string
from urllib.parse import urlparse, parse_qs
from flask import cli, Flask, render_template, request
from werkzeug.exceptions import HTTPException
import requests

from const import (
    SCOPES,
    AUDIENCES,
    TESLA_AUTH_ENDPOINTS,
    TESLA_AK_ENDPOINTS,
)

app = Flask(__name__)

DOMAIN = os.environ['DOMAIN']
DEBUG = os.environ['DEBUG']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
REGION = os.environ['REGION']
AUDIENCE = AUDIENCES[REGION]
TESLA_AUTH_ENDPOINT = TESLA_AUTH_ENDPOINTS[REGION]
TESLA_AK_ENDPOINT = TESLA_AK_ENDPOINTS[REGION]

BLUE = "\u001b[34m"
RESET = "\x1b[0m"

if DEBUG == 'true':
    log_level = logging.DEBUG
else:
    log_level = logging.INFO
logging.basicConfig(format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s',
    level=log_level, datefmt='%H:%M:%S')
logger = logging.getLogger('webui')

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
    randomstate = ''.join(random.choices(string.hexdigits.lower(), k=10))
    randomnonce = ''.join(random.choices(string.hexdigits.lower(), k=10))

    return render_template('index.html', slug=slug, domain=DOMAIN, client_id=CLIENT_ID,
        scopes=SCOPES, randomstate=randomstate, randomnonce=randomnonce,
        auth_endpoint=TESLA_AUTH_ENDPOINT, ak_endpoint=TESLA_AK_ENDPOINT)


@app.route('/callback')
def callback():
    """Handle callback from Tesla server to complete OAuth"""

    url = request.args.get('callback_url')
    app.logger.debug('Callback URL: %s', url)
    # sometimes I don't get a valid code, not sure why
    try:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        code = query_params['code'][0]
        app.logger.debug('code: %s', code)
    except KeyError:
        return 'Invalid code!', 400

    # Exchange code for refresh_token
    req = requests.post(f"{TESLA_AUTH_ENDPOINT}/oauth2/v3/token",
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
    if req.status_code >= 400:
        logger.error("HTTP %s: %s", req.status_code, req.reason)
    response = req.json()
    refresh_token = response['refresh_token']
    app.logger.warning("Obtained refresh token: %s", refresh_token)

    with open('/data/refresh_token', 'w') as f:
        f.write(response['refresh_token'])
    with open('/data/access_token', 'w') as f:
        f.write(response['access_token'])

    return render_template('callback.html', refresh_token=refresh_token)


if __name__ == '__main__':
    logger.info('Starting Flask server for Web UI...')
    cli.show_server_banner = lambda *_: None
    app.run(port=8099, debug=False, host='0.0.0.0')
