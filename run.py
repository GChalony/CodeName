# ### LOGGER ###
# Logging config (could move to config file)
import logging

from flask import request, session
from flask_session import Session
from flask_socketio import SocketIO

from codenameapp import app
from codenameapp.game import Game, GameNamespace
from codenameapp.room import RoomNamespace

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting app!")
logging.getLogger('werkzeug').setLevel(logging.ERROR)

### SESSION ###
Session(app)  # Instanciate session to store data to filesystem
socketio = SocketIO(app, manage_session=False)  # Let flask-session handle sessions


g = Game(["greg", "clem", "sol", "axel"], [["greg", "clem"], ["sol", "axel"]])
games = {"0": g}
temp_default_teams = [["Greg", "Sol"], ["Axel", "Clem"]]

# ### GENERAL SOCKET CALLBACKS  ###
@socketio.on("connect")
def handle_connect():
    # Have access to session here
    logger.debug(f"Socket {request.sid} (user {session.get('pseudo', None)}) connected!")

### ADD SOCKETIO EVENT LISTENERS ###
socketio.on_namespace(RoomNamespace("/room", games.update))
socketio.on_namespace(GameNamespace("/game"))

if __name__ == "__main__":
    socketio.run(app, debug=True)
