import logging

from flask import Flask, render_template, request, \
    url_for
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room

import config
from codenameapp.game import Game
from codenameapp.socket_namespaces import RoomNamespace, GameNamespace
from codenameapp.utils import parse_cell_code, genid

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting app!")
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
app.config.from_object(config)
Session(app)
socketio = SocketIO(app, manage_session=False)


g = Game(["greg", "clem", "sol", "axel"], [["greg", "clem"], ["sol", "axel"]])
games = {"0": g}

temp_default_teams = [["Greg", "Sol"], ["Axel", "Clem"]]

users = []

@app.route("/index")
@app.route("/")
def get_home():
    return render_template("index.html")


@app.route("/<room_id>/grid")
def get_grid(room_id):
    return render_template("grid.html", data=games[room_id].words, teams=temp_default_teams)


@app.route("/<room_id>/room")
def get_room(room_id):
    return render_template("room.html")

@app.route("/<room_id>/cell")
def get_cell_data(room_id):
    cell_code = request.args.get("code")
    r, c = parse_cell_code(cell_code)
    val = games[room_id].answers[r, c]
    logger.debug(f"Returning value for cell {cell_code} : {val}")
    return str(val)


### SOCKET CALLBACKS  ###

@socketio.on("disconnect")
def handle_disconnect():
    print(f"User {request.sid} disconnected!")


@socketio.on("create room")
def handle_create_room(data):
    room_id = genid()
    join_room(room_id)
    room_url = f"{room_id}/room"
    emit("url redirection", {"url": room_url}, broadcast=True)


@socketio.on("return home")
def handle_start_game():
    emit("url redirection", {"url": url_for("get_home")})


socketio.on_namespace(RoomNamespace("room/"))
socketio.on_namespace(GameNamespace("game/"))

if __name__ == "__main__":
    socketio.run(app, debug=True)
