from flask import Flask, render_template, session, request, \
    copy_current_request_context, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
# from werkzeug.utils import redirect
from flask_session import Session
import logging

import config
from codenameapp.utils import generate_random_words, parse_cell_code, generate_response_grid, genid
from codenameapp.users import User

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting app!")
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
app.config.from_object(config)
Session(app)
socketio = SocketIO(app, manage_session=False)


grid = generate_random_words("ressources/words.csv")
grid_response = generate_response_grid()

grids = {"0": grid}
grids_response = {"0": grid_response}

users = []

@app.route("/index")
@app.route("/")
def get_home():
    return render_template("index.html")

@app.route("/<room_id>/grid")
def get_grid(room_id):
    return render_template("grid.html", data=grids[room_id])

@app.route("/<room_id>/room")
def get_room(room_id):
    return render_template("room.html")

@app.route("/cell")
def get_cell_data():
    cell_code = request.args.get("code")
    r, c = parse_cell_code(cell_code)
    val = grid_response[r, c]
    logger.debug(f"Returning value for cell {cell_code} : {val}")
    return str(val)


### SOCKET CALLBACKS  ###

@socketio.on("connect")
def handle_connect():
    if "user_id" in session:
        print(f'Welcome back user {session["user_id"]} !')
    else:
        session_id = request.sid
        session["user_id"] = session_id
        print(f'New user {session["user_id"]} connected!')
        new_user = User(session_id)
        users.append(new_user)
    
# @socketio.on("disconnect")
# def handle_disconnect():
#     print(f"User {request.sid} disconnected!")

@socketio.on("disconnect_request")
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()
    print(f"User {session.get('user_id')} disconnected!")
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit("my_response", {"data": "Disconnected!"}, callback=can_disconnect)

@socketio.on("message")
def handle_message(message):
    print(message)
    emit("message response", request.sid[:5] + " : "+message["msg"], broadcast=True)

@socketio.on("create room")
def handle_create_room(data):
    room_id = genid()
    store_id_in_grid(room_id)
    join_room(room_id)
    room_url = f"{room_id}/room"
    emit("url redirection", {"url": room_url}, broadcast=True)

@socketio.on("join")
def join(room_id):
    join_room(room_id)
    emit("my_response", {"data": "In rooms: " + ", ".join(rooms())})

@socketio.on("start game")
def handle_start_game(data):
    room_url = data["current_url"]
    grid_url = room_url.replace("room", "grid")
    emit("url redirection", {"url": grid_url}, broadcast=True)

@socketio.on("return home")
def handle_start_game():
    emit("url redirection", {"url": url_for("get_home")})


### HELPERS FUNCTIONS ###

def get_user_by_sid(user_id):
    for user in users:
        if user.id == user_id:
            return user
    return None

def store_id_in_grid(room_id):
    grid = generate_random_words("ressources/words.csv")
    grid_response = generate_response_grid()
    grids[room_id] = grid
    grids_response[room_id] = grid_response

if __name__ == "__main__":
    # socketio.run(app, host="0.0.0.0", port=80, debug=True)
    socketio.run(app, debug=True)
