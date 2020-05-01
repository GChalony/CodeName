import datetime
from uuid import uuid4
from flask import render_template, request, redirect, session

from codenameapp import app, logger
from codenameapp.game import Game
from codenameapp.utils import parse_cell_code

g = Game(["greg", "clem", "sol", "axel"], [["greg", "clem"], ["sol", "axel"]])
games = {"0": g}

temp_default_teams = [["Greg", "Sol"], ["Axel", "Clem"]]


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
    # return render_template("grid.html", data=games[room_id].words, teams=temp_default_teams)
    return render_template("grid.html", data=games["0"].words, teams=temp_default_teams)


@app.route("/<room_id>/room")
def get_room(room_id):
    logger.debug(session)
    return render_template("room.html", initial_player_pseudo=session.get("pseudo", None))

@app.route("/<room_id>/cell")
def get_cell_data(room_id):
    cell_code = request.args.get("code")
    r, c = parse_cell_code(cell_code)
    val = games[room_id].answers[r, c]
    # logger.debug(f"Returning value for cell {cell_code} : {val}")
    return str(val)
