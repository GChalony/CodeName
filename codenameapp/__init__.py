from flask import Flask, render_template
import config

### FLASK APP ###
app = Flask(__name__)
app.config.from_object(config)

### IMPORT ROUTES ###
from codenameapp.routes import *
