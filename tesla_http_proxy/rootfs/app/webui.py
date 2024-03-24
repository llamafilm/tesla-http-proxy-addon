import os
import logging
from flask import cli, Flask, render_template
from werkzeug.exceptions import HTTPException

logging.basicConfig(format='[%(asctime)s] %(name)s:%(levelname)s: %(message)s',
    level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger('webui')

app = Flask(__name__)

DOMAIN = os.environ['DOMAIN']

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
    return render_template('index.html', slug=slug, domain=DOMAIN)


if __name__ == '__main__':
    logger.info('Starting Flask server for Web UI...')
    cli.show_server_banner = lambda *_: None
    app.run(port=8099, debug=False, host='0.0.0.0')
