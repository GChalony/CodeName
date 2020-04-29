import logging
<<<<<<< HEAD
from flask import Flask, render_template, request, url_for, redirect, session
=======

from flask import Flask, request, \
    session
>>>>>>> f7e42ee1fca8f6b180ae41e4c4ab5430121ded68
from flask_session import Session
from flask_socketio import SocketIO

import config
<<<<<<< HEAD
from codenameapp.game import Game
from codenameapp.socket_namespaces import RoomNamespace, GameNamespace
from codenameapp.utils import parse_cell_code, genid

from codenameapp import app

### LOGGER ###
=======
from codenameapp.game import Game, GameNamespace
from codenameapp.room import RoomNamespace
from codenameapp.routes import routes_blueprint
from codenameapp.routes import index

# Logging config (could move to config file)
>>>>>>> f7e42ee1fca8f6b180ae41e4c4ab5430121ded68
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting app!")
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# ### FLASK APP ###
# app = Flask(__name__)
# app.config.from_object(config)

<<<<<<< HEAD
### SESSION ###
Session(app)
socketio = SocketIO(app, manage_session=False)
=======
Session(app)  # Instanciate session to store data to filesystem
socketio = SocketIO(app, manage_session=False)  # Let flask-session handle sessions
>>>>>>> f7e42ee1fca8f6b180ae41e4c4ab5430121ded68


g = Game(["greg", "clem", "sol", "axel"], [["greg", "clem"], ["sol", "axel"]])
games = {"0": g}
temp_default_teams = [["Greg", "Sol"], ["Axel", "Clem"]]

### GENERAL SOCKET CALLBACKS  ###
@socketio.on("connect")
def handle_connect():
    # Have access to session here
    logger.debug(f"Socket {request.sid} (user {session.get('pseudo', None)}) connected!")

<<<<<<< HEAD
### ADD SOCKETIO EVENT LISTENERS ###
=======

@socketio.on("disconnect")
def handle_disconnect():
    logger.debug(f"Socket {request.sid} (user {session.get('pseudo', None)}) disconnected!")


>>>>>>> f7e42ee1fca8f6b180ae41e4c4ab5430121ded68
socketio.on_namespace(RoomNamespace("/room", games.update))
socketio.on_namespace(GameNamespace("/game"))

if __name__ == "__main__":
    socketio.run(app, debug=True)
