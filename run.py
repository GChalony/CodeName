import datetime
import logging
from flask import Flask, render_template, request, url_for, redirect, session
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room

import config
from codenameapp.game import Game
from codenameapp.socket_namespaces import RoomNamespace, GameNamespace
from codenameapp.utils import parse_cell_code, genid

from codenameapp import app

### LOGGER ###
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting app!")
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# ### FLASK APP ###
# app = Flask(__name__)
# app.config.from_object(config)

### SESSION ###
Session(app)
socketio = SocketIO(app, manage_session=False)


g = Game(["greg", "clem", "sol", "axel"], [["greg", "clem"], ["sol", "axel"]])
games = {"0": g}
temp_default_teams = [["Greg", "Sol"], ["Axel", "Clem"]]


### ADD SOCKETIO EVENT LISTENERS ###
socketio.on_namespace(RoomNamespace("/room", games.update))
socketio.on_namespace(GameNamespace("/game"))

if __name__ == "__main__":
    socketio.run(app, debug=True)
