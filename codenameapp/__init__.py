from flask import Flask
import logging

import config

### LOGGER ###
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting app!")
logging.getLogger('werkzeug').setLevel(logging.ERROR)

### FLASK APP ###
app = Flask(__name__)
app.config.from_object(config)

### IMPORT ROUTES ###
from codenameapp.routes import *
