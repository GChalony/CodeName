import logging

from flask import session, request
from flask_socketio import Namespace, emit, join_room, leave_room, \
    close_room, rooms, disconnect, send
import logging
from uuid import uuid4

from server.game import Game
from server.room_session import room_session
from server.users import User

logger = logging.getLogger(__name__)

temp_default_teams = [[User("1", "Greg"), User("2", "Sol")],
                      [User("3", "Clem"), User("4", "Axel")]]

class RoomNamespace(Namespace):
    def __init__(self, name):
        super(RoomNamespace, self).__init__(name)

    def on_connect(self):
        # Have access to session here
        # logger.debug(f'Socket {request.sid} (user {session.get("pseudo", None)}) connected!')
        # logger.debug("Connected to room Namespace!")

        if not hasattr(room_session, "users"):  # First connection
            room_session.users = []
        if "user_id" in session:
            print("WELCOME BACK", session["user_id"])
        user_id = session.get("user_id", uuid4().hex)
        session["user_id"] = user_id
        pseudo = session.get("pseudo", "")
        session["pseudo"] = pseudo
        backcol = session.get("backcol", "#ffff00")
        session["backcol"] = backcol
        mouthcol = session.get("mouthcol", "#ff0000")
        session["mouthcol"] = mouthcol

        old_user = self.get_user_by_id(user_id)
        if not old_user:
            print("NEW USER, pseudo=", pseudo)
            new_user = User(user_id, pseudo, backcol, mouthcol)
            room_session.users.append(new_user)
        print("ON CONNECT room_session.users", room_session.users)
        # logger.debug(room_session.__dict__)

    def on_disconnect(self):
        logger.debug("Disconnected from room Namespace!")
        user_id = session.get("user_id", None)
        user = self.get_user_by_id(user_id)
        if user:
            room_session.users.remove(user)

    def get_user_by_id(self, user_id):
        for u in room_session.users:
            if u.id == user_id:
                return u

    def on_start_game(self):
        logger.info("start game")
        room_session.teams = temp_default_teams
        url = request.environ["HTTP_REFERER"]  # Access to request context
        grid_url = url.replace("room", "grid")
        game = Game([[u.id for u in team] for team in room_session.teams])
        room_session.game = game
        emit("url_redirection", {"url": grid_url}, broadcast=True)


    def on_create_room(self, data):
        print("on_create_room, data=", data)
        new_room_id = uuid4().hex
        data["room_id"] = new_room_id
        self.on_join_existing_room(data)

    def on_join_existing_room(self, data):
        print("on_join_existing_room, data=", data)
        room_id = data.get("room_id")
        user_id = session.get("user_id")
        user = self.get_user_by_id(user_id)

        pseudo = data.get("pseudo")
        backcol = data.get("backcol")
        mouthcol = data.get("mouthcol")
        session["pseudo"] = pseudo
        session["backcol"] = backcol
        session["mouthcol"] = mouthcol
        session["user_id"] = user_id
        print("ON JOIN, pseudo=", pseudo)
        print("ON JOIN, session['pseudo']=", session['pseudo'])
        user.pseudo = pseudo
        user.backcol = backcol
        user.mouthcol = mouthcol

        join_room(room_id)
        print("rooms()", rooms())
        room_url = f"{room_id}/room"
        emit("url_redirection", {"url": room_url})

    def on_leave_room(self, data):
        user_id = session.get("user_id")
        current_url = data["current_url"]
        room_id = current_url.split("/")[-2]
        user = self.get_user_by_id(user_id)
        print("on_leave_room, user_id=", user_id)
        print("on_leave_room, user=", user)
        print("on_leave_room, room_session.users=", room_session.users)
        if user:
            room_session.users.remove(user)
        leave_room(room_id)
        print("on_leave_room, rooms()=", rooms())
        emit("url_redirection", {"url": "/"})
        self.on_get_players_in_room()

    def on_close_room(self, data):
        room_id = data["room_id"]
        print("on_close_room")
        # emit("my_response", {"data": "Room " + room + " is closing.", room=room)
        close_room(room_id)

    def on_my_room_event(self, message):
        emit("my_response", {"data": message["data"]}, room=message["room"])

    def on_get_players_in_room(self):
        print("on_get_players_in_room")
        # current_url = data["current_url"]
        # room_id = current_url.split("/")[-2]
        players_list = [user.__dict__ for user in room_session.users]
        emit("response_players_in_room", {"players": players_list}, broadcast=True)

    def on_get_user_infos(self):
        user_id = session.get("user_id")
        user = self.get_user_by_id(user_id)
        print("on_get_user_infos, user=", user)
        print("on_get_user_infos, user.backcol=", user.backcol)
        # pseudo = "pas de pseudo"
        if user:
            print("user.pseudo", user.pseudo)
            pseudo = user.pseudo
            backcol = user.backcol
            mouthcol = user.mouthcol
            emit("return_user_infos", {"pseudo": pseudo, "backcol": backcol, "mouthcol": mouthcol})
        else:
            print("YA PAS DE USER on get user info")

    def on_debug_button(self, data):
        print("on_debug_button")
        current_url = data["current_url"]
        room_id = current_url.split("/")[-2]