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

# Logging config (could move to config file)
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting app!")
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
app.config.from_object(config)
Session(app)  # Instanciate session to store data to filesystem
socketio = SocketIO(app, manage_session=False)  # Let flask-session handle sessions


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
    # Should store this room id somewhere, and possibly the user who created it

    logger.debug(f"Created new room {room_id}")
    pseudo = request.args.get("pseudo", None)
    col1 = request.args.get("col1", None)
    col2 = request.args.get("col2", None)

    if pseudo is None or col1 is None or col2 is None:
        return "Missing parameters", 400

    user_id = session.get("user_id", uuid4().hex)  # Create new user_id if not already stored
    session["user_id"] = user_id
    session["pseudo"] = pseudo
    session["avatar-col1"] = col1
    session["avatar-col2"] = col2

    # Here we should store the user in DB and in a dict or smth

    resp = redirect(f"{room_id}/room")
    # Add cookies (could attach them to the home page to avoid sending them all the time...)
    expire_date = datetime.datetime.now() + datetime.timedelta(30)  # 30 days ahead
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
    logger.debug(session)
    return render_template("room.html", initial_player_pseudo=session.get("pseudo", None))


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
