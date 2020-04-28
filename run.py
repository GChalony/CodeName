import logging
# from uuid import uuid4

from flask import Flask, render_template, request, \
    url_for, redirect
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room

import config
from codenameapp.game import Game
from codenameapp.socket_namespaces import RoomNamespace, GameNamespace
from codenameapp.utils import parse_cell_code, genid
# from codenameapp import routes
# from codenameapp.routes import *
from flask import Flask
from codenameapp.routes import routes_blueprint
# from routes2 import routes_blueprint

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting app!")
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
app.config.from_object(config)
app.register_blueprint(routes_blueprint)

Session(app)
socketio = SocketIO(app, manage_session=False)


g = Game(["greg", "clem", "sol", "axel"], [["greg", "clem"], ["sol", "axel"]])
games = {"0": g}

temp_default_teams = [["Greg", "Sol"], ["Axel", "Clem"]]


# @app.route("/index")
# @app.route("/")
# def get_home():
#     return render_template("index.html")

# @app.route("/new_room")
# def create_new_room():
#     room_id = uuid4()
#     print(f"Created new room {room_id}")
#     return redirect(f"{room_id}/room")

# @app.route("/<room_id>/grid")
# def get_grid(room_id):
#     return render_template("grid.html", data=games[room_id].words, teams=temp_default_teams)

# @app.route("/<room_id>/room")
# def get_room(room_id):
#     return render_template("room.html")

# @app.route("/<room_id>/cell")
# def get_cell_data(room_id):
#     cell_code = request.args.get("code")
#     r, c = parse_cell_code(cell_code)
#     val = games[room_id].answers[r, c]
#     logger.debug(f"Returning value for cell {cell_code} : {val}")
#     return str(val)


socketio.on_namespace(RoomNamespace("/room", games.update))
socketio.on_namespace(GameNamespace("/game"))

if __name__ == "__main__":
    socketio.run(app, debug=True)
