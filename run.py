#!/usr/bin/env python
import logging

from engineio.payload import Payload
from flask import Flask
from flask_session import Session
from flask_socketio import SocketIO

import config
from codenameapp.game.game_manager import GameManager
from codenameapp.routes import RouteManager
from codenameapp.waiting_room.room_manager import RoomManager

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


if __name__ == '__main__':
    socketio.run(app, debug=True)
