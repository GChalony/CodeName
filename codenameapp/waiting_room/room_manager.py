import datetime
import logging
from uuid import uuid4

from flask import render_template, request, session
from flask_socketio import emit, join_room, rooms, leave_room, close_room
from flask_socketio import Namespace
from werkzeug.utils import redirect

from codenameapp.game.game import Game
from codenameapp.models import User, Team
from codenameapp.room_session import room_session, emit_in_room, get_room_id

logger = logging.getLogger(__name__)


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

        resp = redirect(f"{room_id}/room")
        # Add cookies
        expire_date = datetime.datetime.now() + datetime.timedelta(30)  # 30 days ahead
        resp.set_cookie("user_id", user_id, expires=expire_date)
        resp.set_cookie("pseudo", pseudo, expires=expire_date)
        resp.set_cookie("avatar-col1", col1, expires=expire_date)
        resp.set_cookie("avatar-col2", col2, expires=expire_date)
        return resp

    def get_room(self, room_id):
        # TODO add button only for room creator
        return render_template("room.html")

    def notify_team_change(self):
        # Send event in room about new teams (or changes only ?)
        emit_in_room("teams_changed", room_session.teams.to_dict())

    def on_connect(self):
        # Initialize teams if first connection
        if not hasattr(room_session, "teams"):
            room_session.teams = (Team(), Team())
        join_room(get_room_id())
        # Assign user to some position / team
        user = User(session["user_id"], session["pseudo"], session["avatar-col1"],
                    session["avatar-col2"])
        self._add_to_available_position(user)
        # Notify team change
        self.notify_team_change()

    def on_disconnect(self):
        # Remove user from team
        user_id = session["user_id"]
        self._pop_user_by_id(user_id)
        # Notify team change
        self.notify_team_change()

    def on_change_position(self, new_pos):
        # new_pos: 0: team red, spy - 1: team red, guesser -
        #           2: team blue, spy - 3: team blue, guesser
        (tred, tblue) = room_session.teams
        user = self._pop_user_by_id(session["user_id"])
        # Check that position is available before changing
        flag = False
        if new_pos == 0:
            if tred.spy is None:
                flag = False
            else:
                tred.spy = user
                flag = True
        elif new_pos == 1:
            tred.guessers.append(user)
            flag = True
        elif new_pos == 2:
            if tblue.spy is None:
                flag = False
            else:
                tblue.spy = user
                flag = True
        elif new_pos == 1:
            tblue.guessers.append(user)
            flag = True
        # Notify
        self.notify_team_change()
        return flag

    def on_start_game(self):
        # Check that teams are ok
        # Store teams ..?
        # Emit URL redirection
        pass

    def _add_to_available_position(self, user):
        (tred, tblue) = room_session.teams()
        if tred.spy is None:
            tred.spy = user
        elif tblue.spy is None:
            tblue.spy = user
        elif len(tred.guessers) <= len(tblue.guessers):
            tred.guessers.append(user)
        else:
            tblue.guessers.append(user)

    def _pop_user_by_id(self, user_id):
        for team in room_session.teams:
            if team.spy.id == user_id:
                team.spy = None
                return team.spy
            for u in team.guessers:
                if u.id == user_id:
                    team.guessers.remove(u)
                    return u