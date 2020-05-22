#!/usr/bin/env python
import logging

from engineio.payload import Payload
from flask import Flask
from flask_mail import Mail
from flask_session import Session
from flask_socketio import SocketIO

import config
from codenameapp.game.game import Game
from codenameapp.game.game_manager import GameManager
from codenameapp.waiting_room.room_manager import RoomManager
from codenameapp.room_session import room_session
from codenameapp.routes import RouteManager
from codenameapp.models import User

logging.basicConfig(level=logging.WARNING,
                    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("codenameapp").setLevel(logging.DEBUG)
logger.info("Starting app!")

logging.getLogger("werkzeug").setLevel(logging.ERROR)

# To remove error about packets
Payload.max_decode_packets = 50


# FLASK APP
app = Flask(__name__)
Mail(app)
app.config.from_object(config.default_config)

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

room_manager = RoomManager('/room')
room_manager.init_routes(app)
socketio.on_namespace(room_manager)

route_manager = RouteManager()
route_manager.init_routes(app)

game_manager = GameManager('/grid')
game_manager.init_routes(app)
socketio.on_namespace(game_manager)


if __name__ == '__main__':
    socketio.run(app, debug=True)
