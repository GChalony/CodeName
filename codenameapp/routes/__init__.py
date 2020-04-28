"""Routes"""

# from os.path import dirname, basename, isfile
# import glob
# modules = glob.glob(dirname(__file__)+"/*.py")
# __all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

# print("__all__", __all__)

from flask import Flask, render_template, request, \
    url_for, redirect, Blueprint
from uuid import uuid4

routes_blueprint = Blueprint('routes_blueprint', __name__)
from .index import *
from codenameapp.game import Game
from codenameapp.socket_namespaces import RoomNamespace, GameNamespace
from codenameapp.utils import parse_cell_code, genid

g = Game(["greg", "clem", "sol", "axel"], [["greg", "clem"], ["sol", "axel"]])
games = {"0": g}

temp_default_teams = [["Greg", "Sol"], ["Axel", "Clem"]]



@routes_blueprint.route("/new_room")
def create_new_room():
    room_id = uuid4()
    print(f"Created new room {room_id}")
    return redirect(f"{room_id}/room")

@routes_blueprint.route("/<room_id>/grid")
def get_grid(room_id):
    return render_template("grid.html", data=games[room_id].words, teams=temp_default_teams)

@routes_blueprint.route("/<room_id>/room")
def get_room(room_id):
    return render_template("room.html")

@routes_blueprint.route("/<room_id>/cell")
def get_cell_data(room_id):
    cell_code = request.args.get("code")
    r, c = parse_cell_code(cell_code)
    val = games[room_id].answers[r, c]
    # logger.debug(f"Returning value for cell {cell_code} : {val}")
    return str(val)
