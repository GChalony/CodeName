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
        # Track ALL users
        # I don't think we actually need that (just users of one room_id)
        self.users = []
        self.all_rooms = {}
        self.all_users = {}

    def on_connect(self):
        # Have access to session here
        # logger.debug(f'Socket {request.sid} (user {session.get("pseudo", None)}) connected!')
        # logger.debug("Connected to room Namespace!")
        user_id = session.get("user_id", uuid4().hex)
        session["user_id"] = user_id
        # if "user_id" not in session:
        #     # There is a better way to handle errors in sockets
        #     raise Exception("No user_id!")

        user_id = session["user_id"]
        pseudo = session.get("pseudo", "mypseudo")
        session["pseudo"] = pseudo

        # logger.info(f'Welcome back user {user_id} - {pseudo} !')
        new_user = User(user_id, pseudo)
        if not hasattr(room_session, "users"):  # First connection
            room_session.users = []
        room_session.users.append(new_user)
        # logger.debug(room_session.__dict__)

    def on_disconnect(self):
        logger.debug("Disconnected from room Namespace!")
        user_id = session.get("user_id", None)
        i, user = self.get_user_by_id(user_id)
        room_session.users.pop(i)

    def get_user_by_id(self, user_id):
        for i, u in enumerate(room_session.users):
            if u.id == user_id:
                return i, u

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
        if new_room_id not in self.all_rooms:
            self.all_rooms[new_room_id] = []
        data["room_id"] = new_room_id
        self.on_join_existing_room(data)

    def on_join_existing_room(self, data):
        print("on_join_existing_room, data=", data)
        room_id = data.get("room_id")
        user_id = session.get("user_id", uuid4().hex)
        if room_id not in self.all_rooms:
            print("ROOM_ID DOES NOT EXIST") # Need to display this to player
        elif user_id not in self.all_rooms[room_id]:
            self.all_rooms[room_id].append(user_id) # register user_id in all_rooms[room_id]

        nickname = data.get("nickname")
        session["pseudo"] = nickname
        session["user_id"] = user_id
        if user_id not in self.all_users:
            self.all_users[user_id] = [room_id] # register room_id in all_users[user_id]
        else:
            self.all_users[user_id].append(room_id)

        print("self.all_rooms", self.all_rooms)
        join_room(room_id)
        print("rooms()", rooms())
        room_url = f"{room_id}/room"
        emit("url_redirection", {"url": room_url})
        print("ALL PLAYERS : self.all_rooms[room_id]", self.all_rooms[room_id])
        emit("get_players_in_room", {"players": self.all_rooms[room_id]})


    def on_leave_room(self, data):
        user_id = session.get("user_id")
        current_url = data["current_url"]
        room_id = current_url.split("/")[-2]
        if room_id in self.all_users[user_id]:
            self.all_users[user_id].remove(room_id)
        if user_id in self.all_rooms[room_id]:
            self.all_rooms[room_id].remove(user_id)
        leave_room(room_id)
        print("on_leave_room, self.all_users=", self.all_users)
        print("on_leave_room, self.all_rooms=", self.all_rooms)
        print("on_leave_room, rooms()=", rooms())
        if not self.all_rooms[room_id]:
            self.on_close_room({"room_id": room_id})
        emit("url_redirection", {"url": "/"})

    def on_close_room(self, data):
        room_id = data["room_id"]
        del self.all_rooms[room_id]
        print("on_close_room, self.all_rooms=", self.all_rooms)
        # emit("my_response", {"data": "Room " + room + " is closing.", room=room)
        close_room(room_id)

    def on_my_room_event(self, message):
        emit("my_response", {"data": message["data"]}, room=message["room"])

    def on_debug_button(self, data):
        print("on_debug_button")
        a = request.cookies.get("user_id")
        b = request.cookies.get("pseudo")
        c = request.cookies.get("avatar-col1")
        d = request.cookies.get("avatar-col2")
        print(a, b, c, d)

        current_url = data["current_url"]
        room_id = current_url.split("/")[-2]
        emit("get_players_in_room", {"players": self.all_rooms[room_id]})
