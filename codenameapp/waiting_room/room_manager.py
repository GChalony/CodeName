import datetime
import logging
from uuid import uuid4

from flask import render_template, request, session
from flask_socketio import join_room
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

    def init_room(self):
        logger.debug("Initiating waiting room!")
        room_session.teams = (Team(), Team())
        room_session.creator = session["user_id"]
        room_session.started = False

    def get_room(self, room_id):
        if not hasattr(room_session, "teams"):
            self.init_room()

        return render_template("room.html",
                               teams=room_session.teams,
                               is_creator=session["user_id"] == room_session.creator)

    def notify_team_change(self):
        logger.debug(f"Sending teams={room_session.teams}")
        # Send event in room about new teams (or changes only ?)
        emit_in_room("teams_changed", {i: t.to_json() for i, t in enumerate(room_session.teams)},
                     broadcast=True)
        emit_in_room("toggle_start", self._are_teams_ready())

    def on_connect(self):
        logger.debug(f"User {session['pseudo']} connected! (sid={request.sid})")
        # Initialize teams if first connection
        join_room(get_room_id())
        # Assign user to some position / team
        user = User(session["user_id"], session["pseudo"], session["avatar-col1"],
                    session["avatar-col2"])
        if self._get_user_by_id(session["user_id"]) is None:
            self._add_to_available_position(user)
        # Notify team change
        self.notify_team_change()

    def on_disconnect(self):
        # Check if disconnected because of game starting or smth else
        if not room_session.started:
            # TODO handle creator disconnect: assign to someone else, close room ..?
            # Remove user from team
            user_id = session["user_id"]
            self._pop_user_by_id(user_id)
            # Notify team change
            self.notify_team_change()

    def on_change_position(self, new_pos):
        new_pos = int(new_pos)
        # new_pos: 0: team red, spy - 1: team red, guesser -
        #           2: team blue, spy - 3: team blue, guesser
        (tred, tblue) = room_session.teams
        logger.debug(f"Teams={room_session.teams}")
        user_id = session["user_id"]
        user = self._get_user_by_id(user_id)
        logger.debug(f"Changing pos to {new_pos} for user {user}")
        # Check that position is available before changing (though should never happen that not)
        if new_pos == 0:
            if tred.spy is None:
                tred.spy = user
                self._pop_user_by_id(user_id)
            else:
                logger.warning(f"User {user} asking to change to occupied position {new_pos} ("
                               f"({tred.spy})")
        elif new_pos == 1:
            tred.guessers.append(user)
            self._pop_user_by_id(user_id)
        elif new_pos == 2:
            if tblue.spy is None:
                tblue.spy = user
                self._pop_user_by_id(user_id)
            else:
                logger.warning(f"User {user} asking to change to occupied position {new_pos}"
                               f"({tblue.spy})")
        elif new_pos == 3:
            tblue.guessers.append(user)
            self._pop_user_by_id(user_id)
        # Notify
        logger.debug(f"{tred}")
        logger.debug(f"{tblue}")
        self.notify_team_change()

    def on_start_game(self):
        # Check that teams are ok
        if self._are_teams_ready():
            # Emit URL redirection
            logger.info("Starting game !")
            room_session.started = True
            url = request.environ["HTTP_REFERER"]  # Access to request context
            grid_url = url.replace("room", "grid")
            game = Game([team.get_ids_list() for team in room_session.teams])
            room_session.game = game
            emit_in_room("url_redirection", {"url": grid_url}, broadcast=True)
        else:
            logger.debug("Teams not ready yet")

    def _add_to_available_position(self, user):
        (tred, tblue) = room_session.teams
        if tred.spy is None:
            tred.spy = user
        elif tblue.spy is None:
            tblue.spy = user
        elif len(tred.guessers) <= len(tblue.guessers):
            tred.guessers.append(user)
        else:
            tblue.guessers.append(user)

    def _get_user_by_id(self, user_id):
        for i, team in enumerate(room_session.teams):
            if team.spy is not None and team.spy.id == user_id:
                return team.spy
            for u in team.guessers:
                if u.id == user_id:
                    return u

    def _pop_user_by_id(self, user_id):
        for team in room_session.teams:
            if team.spy is not None and team.spy.id == user_id:
                spy = team.spy
                team.spy = None
                return spy
            for u in team.guessers:
                if u.id == user_id:
                    team.guessers.remove(u)
                    return u

    def _are_teams_ready(self):
        # Check have spies and at least one guesser per team
        (tred, tblue) = room_session.teams
        return tred.spy is not None and tblue.spy is not None \
               and len(tred.guessers) and len(tblue.guessers)
