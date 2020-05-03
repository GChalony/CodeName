#!/usr/bin/env python
from flask_socketio import SocketIO
from flask_session import Session
from flask import Flask
import logging
from engineio.payload import Payload

from server.room import RoomNamespace
from server.tuto import TutoNamespace
from server.routes import RouteManager
from server.game import Game
# from server import app
import config

import logging

### LOGGER ###
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting app!")
logging.getLogger("werkzeug").setLevel(logging.ERROR)

# To remove error about packets
Payload.max_decode_packets = 50

### FLASK APP ###
app = Flask(__name__)
app.config.from_object(config)

# use_session = True
use_session = False

if use_session:
    Session(app)
    socketio = SocketIO(app, manage_session=False)
else:
    socketio = SocketIO(app)

g = Game(["greg", "clem", "sol", "axel"], [["greg", "clem"], ["sol", "axel"]])
games = {"0": g}

temp_default_teams = [["Greg", "Sol"], ["Axel", "Clem"]]

room_namespace = RoomNamespace("/room", games.update)
tuto_namespace = TutoNamespace("/tuto")
route_manager = RouteManager(app, tuto_namespace)

socketio.on_namespace(room_namespace)
socketio.on_namespace(tuto_namespace)

if __name__ == "__main__":
    socketio.run(app, debug=True)
