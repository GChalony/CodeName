import logging

from flask import Flask, render_template, request, url_for
from flask_socketio import SocketIO, emit
from werkzeug.utils import redirect

import config
from codenameapp.utils import generate_random_words, parse_cell_code, generate_response_grid, genid

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting app!")

app = Flask(__name__)
app.config.from_object(config)
socketio = SocketIO(app)

grid = generate_random_words("ressources/words.csv")
grid_response = generate_response_grid()

grids = {"0": grid}
grids_response = {"0": grid_response}


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


@app.route("/new")
def new_game():
    room_id = genid()
    grid = generate_random_words("ressources/words.csv")
    grid_response = generate_response_grid()
    grids[room_id] = grid
    grids_response[room_id] = grid_response
    return redirect(f"{room_id}/room")


@app.route("/cell")
def get_cell_data():
    cell_code = request.args.get("code")
    r, c = parse_cell_code(cell_code)
    val = grid_response[r, c]
    logger.debug(f"Returning value for cell {cell_code} : {val}")
    return str(val)

# Socket callbacks
@socketio.on("connect")
def handle_connect():
    print(f"User {request.sid} connected!")

@socketio.on("disconnect")
def handle_disconnect():
    print(f"User {request.sid} disconnected!")

@socketio.on("message")
def handle_message(message):
    print(message)
    emit("message response", request.sid[:5] + " : "+message["msg"], broadcast=True)

@socketio.on("start game")
def handle_start_game(data):
    room_url = data["current_url"]
    grid_url = room_url.replace("room", "grid")
    emit("url redirection", {"url": grid_url}, broadcast=True)

@socketio.on("return home")
def handle_start_game():
    emit("url redirection", {"url": url_for("get_home")})


if __name__ == "__main__":
    # socketio.run(app, host="0.0.0.0", port=80, debug=True)
    socketio.run(app, debug=True)
