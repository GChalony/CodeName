import datetime
import logging
from uuid import uuid4

from flask import render_template, request, session
from flask_socketio import emit, join_room, rooms, leave_room, close_room
from flask_socketio import Namespace
from werkzeug.utils import redirect

from codenameapp.game.game import Game
from codenameapp.models import User
from codenameapp.room_session import room_session

logger = logging.getLogger(__name__)

temp_default_teams = [[User("1", "Greg"), User("2", "Sol")],
                      [User("3", "Clem"), User("4", "Axel")]]

team_number_from_color = {
    "red": 0,
    "blue": 1
}

room_teams_default = {
    "red": [
        None,
        None,
        None,
        None
    ],
    "blue": [
        None,
        None,
        None,
        None
    ]
}


class RoomManager(Namespace):
    def __init__(self, name):
        super(RoomManager, self).__init__(name)

    def init_routes(self, app):
        app.add_url_rule('/new_room', view_func=self.create_new_room)
        app.add_url_rule('/<room_id>/room', view_func=self.get_room)

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

    def notify_team_change(self):
        # Send event in room about new teams (or changes only ?)
        pass

    def on_connect(self):
        # Assign user to some position / team
        # Notify team change
        pass

    def on_disconnect(self):
        # Remove user from team
        # Notify team change
        pass

    def on_change_position(self, new_pos):
        # Check that position is available
        # Set user in new position
        # Notify
        pass

    def on_start_game(self):
        # Check that teams are ok
        # Store teams ..?
        # Emit URL redirection
        pass