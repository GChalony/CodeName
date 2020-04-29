import datetime
import logging
from uuid import uuid4

from flask import Flask, render_template, request, \
    url_for, redirect, session
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room

import config
from codenameapp.game import Game, GameNamespace
from codenameapp.room import RoomNamespace
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



@app.route("/index")
@app.route("/")
def get_home():
    return render_template("index.html")


@app.route("/new_room")
def create_new_room():
    room_id = uuid4().hex
    print(f"Created new room {room_id}")
    pseudo = request.args.get("pseudo", None)
    col1 = request.args.get("col1", "")
    col2 = request.args.get("col2", "")
    resp = redirect(f"{room_id}/room")
    user_id = session.get("user_id", uuid4().hex)

    expire_date = datetime.datetime.now() + datetime.timedelta(30)  # 30 days ahead
    session["user_id"] = user_id
    session["pseudo"] = pseudo
    session["avatar-col1"] = col1
    session["avatar-col2"] = col2
    resp.set_cookie("user_id", user_id, expires=expire_date)
    resp.set_cookie("pseudo", pseudo, expires=expire_date)
    resp.set_cookie("avatar-col1", col1, expires=expire_date)
    resp.set_cookie("avatar-col2", col2, expires=expire_date)
    return resp


@app.route("/<room_id>/grid")
def get_grid(room_id):
    return render_template("grid.html", data=games[room_id].words, teams=temp_default_teams)


@app.route("/<room_id>/room")
def get_room(room_id):
    print(session)
    return render_template("room.html")


@app.route("/<room_id>/cell")
def get_cell_data(room_id):
    cell_code = request.args.get("code")
    r, c = parse_cell_code(cell_code)
    val = games[room_id].answers[r, c]
    logger.debug(f"Returning value for cell {cell_code} : {val}")
    return str(val)


### SOCKET CALLBACKS  ###
@socketio.on("connect")
def handle_connect():
    print(f"Socket {request.sid} connected!")


@socketio.on("disconnect")
def handle_disconnect():
    print(f"Socket {request.sid} disconnected!")


@socketio.on("create room")
def handle_create_room(data):
    room_id = genid()
    join_room(room_id)
    room_url = f"{room_id}/room"
    emit("url redirection", {"url": room_url}, broadcast=True)


socketio.on_namespace(RoomNamespace("/room", games.update))
socketio.on_namespace(GameNamespace("/game"))

if __name__ == "__main__":
    socketio.run(app, debug=True)
