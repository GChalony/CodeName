#!/usr/bin/env python
import logging

from engineio.payload import Payload
from flask import Flask
from flask_session import Session
from flask_socketio import SocketIO

import config
from codenameapp.avatar.avatar_manager import AvatarManager
from codenameapp.game.game_manager import GameManager
from codenameapp.routes import RouteManager
from codenameapp.utils import ColorFormatter
from codenameapp.waiting_room.room_manager import RoomManager

logging.basicConfig(level=logging.WARNING)
logging.root.handlers[0].setFormatter(ColorFormatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
logger = logging.getLogger(__name__)
logging.getLogger("codenameapp").setLevel(logging.DEBUG)
logger.info("Starting app!")

logging.getLogger("werkzeug").setLevel(logging.ERROR)

# To remove error about packets
Payload.max_decode_packets = 50


# FLASK APP
app = Flask(__name__)
app.config.from_object(config.default_config)
Session(app)
socketio = SocketIO(app, manage_session=False)


room_manager = RoomManager('/room')
room_manager.init_routes(app)
socketio.on_namespace(room_manager)

route_manager = RouteManager()
route_manager.init_routes(app)

game_manager = GameManager('/grid')
game_manager.init_routes(app)
socketio.on_namespace(game_manager)

avatar_manager = AvatarManager()
avatar_manager.init_routes(app)


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True)
