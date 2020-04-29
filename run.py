import logging

from flask import Flask, request, \
    session
from flask_session import Session
from flask_socketio import SocketIO

import config
from codenameapp.game import Game, GameNamespace
from codenameapp.room import RoomNamespace
from codenameapp.routes import routes_blueprint
from codenameapp.routes import index

# Logging config (could move to config file)
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting app!")
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
app.config.from_object(config)
app.register_blueprint(routes_blueprint)

Session(app)  # Instanciate session to store data to filesystem
socketio = SocketIO(app, manage_session=False)  # Let flask-session handle sessions


g = Game(["greg", "clem", "sol", "axel"], [["greg", "clem"], ["sol", "axel"]])
games = {"0": g}

temp_default_teams = [["Greg", "Sol"], ["Axel", "Clem"]]

### GENERAL SOCKET CALLBACKS  ###
@socketio.on("connect")
def handle_connect():
    # Have access to session here
    logger.debug(f"Socket {request.sid} (user {session.get('pseudo', None)}) connected!")


@socketio.on("disconnect")
def handle_disconnect():
    logger.debug(f"Socket {request.sid} (user {session.get('pseudo', None)}) disconnected!")


socketio.on_namespace(RoomNamespace("/room", games.update))
socketio.on_namespace(GameNamespace("/game"))

if __name__ == "__main__":
    socketio.run(app, debug=True)
