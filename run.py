#!/usr/bin/env python
import logging

from engineio.payload import Payload
from flask import Flask
from flask_session import Session
from flask_socketio import SocketIO

import config
from server.game import Game
from server.game_manager import GameManager
from server.room import RoomNamespace
from server.room_session import room_session
from server.routes import RouteManager
from server.tuto import TutoNamespace
from server.users import User

logging.basicConfig(level=logging.WARNING,
                    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("server").setLevel(logging.DEBUG)
logger.info("Starting app!")

logging.getLogger("werkzeug").setLevel(logging.ERROR)

# To remove error about packets
Payload.max_decode_packets = 50

### FLASK APP ###
app = Flask(__name__)
app.config.from_object(config)

use_session = True
# use_session = False

if use_session:
    Session(app)
    socketio = SocketIO(app, manage_session=False)
else:
    socketio = SocketIO(app)


temp_default_teams = [[User("1", "Greg"), User("2", "Sol"), User("5", "Vic")],
                      [User("3", "Clem"), User("4", "Axel")]]
g = Game([[u.id for u in team] for team in temp_default_teams])
# Should never do that, this is just to add a default room for tests only
room_session._all_rooms_data["0"] = {"game": g, "teams": temp_default_teams}

room_namespace = RoomNamespace('/room')
tuto_namespace = TutoNamespace('/tuto')

socketio.on_namespace(room_namespace)
socketio.on_namespace(tuto_namespace)

route_manager = RouteManager(app)
route_manager.init_routes()

game_manager = GameManager('/grid')
game_manager.init_routes(app)
socketio.on_namespace(game_manager)


if __name__ == '__main__':
    socketio.run(app)
