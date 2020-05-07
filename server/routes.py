import datetime
import logging
from uuid import uuid4

from flask import render_template, request, redirect, session

from server.room_session import room_session
from server.utils import parse_cell_code

logger = logging.getLogger(__name__)


class RouteManager:
    def __init__(self, app):
        self.app = app

    def init_routes(self):
        self.app.add_url_rule('/tuto', view_func=self.tuto)
        self.app.add_url_rule('/', view_func=self.get_home)
        self.app.add_url_rule('/new_room', view_func=self.create_new_room)
        self.app.add_url_rule('/<room_id>/room', view_func=self.get_room)
        self.app.add_url_rule('/<room_id>/grid', view_func=self.get_grid)
        self.app.add_url_rule('/<room_id>/cell', view_func=self.get_cell_data)

    def tuto(self):
        print("rooms ROUTE", self.all_rooms)
        return render_template("tuto.html")

    def get_home(self):
        return render_template("index.html")

    def create_new_room(self):
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

    def get_room(self, room_id):
        return render_template("room.html")
        # return render_template("room.html", initial_player_pseudo=session.get("pseudo", None))

    def get_grid(self, room_id):
        return render_template("grid.html", words=room_session.game.words, teams=room_session.teams)

    def get_cell_data(self, room_id):
        cell_code = request.args.get("code")
        r, c = parse_cell_code(cell_code)
        val = room_session.game.answers[r, c]
        # logger.debug(f"Returning value for cell {cell_code} : {val}")
        return str(val)
