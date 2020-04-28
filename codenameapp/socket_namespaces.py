from uuid import uuid4

from flask import session, request
from flask_socketio import Namespace, emit

from codenameapp.users import User


class RoomNamespace(Namespace):
    def __init__(self, name):
        super(RoomNamespace, self).__init__(name)
        # Track ALL users
        # I don't think we actually need that
        self.users = []

    def on_connect(self):
        if "user_id" in session:
            print(f'Welcome back user {session["user_id"]} !')
        else:
            session_id = uuid4()
            session["user_id"] = session_id
            print(f'New user {session_id} connected!')
            new_user = User(session_id)
            self.users.append(new_user)

    def on_disconnect(self):
        user_id = session.get("user_id", None)
        i, user = self.get_user_by_id(user_id)
        self.users.pop(i)

    def get_user_by_id(self, user_id):
        for i, u in self.users:
            if u.id == user_id:
                return i, u

    def on_start_game(self):
        url = request.base_url
        grid_url = url.replace("room", "grid")

        # Need to create a Game instance here...
        emit("url redirection", {"url": grid_url}, broadcast=True)


class GameNamespace(Namespace):
    def on_connect(self):
        if "user_id" in session:
            print(f'Welcome back user {session["user_id"]} !')
        else:
            raise Exception("User not authenticated")

    def on_disconnect(self):
        user_id = session.get("user_id", None)
        print(f"User {user_id} left the game !")

    def on_message(self, msg):
        print("Received : "+msg)
        emit("message response", request.sid[:5] + " : " + msg["msg"], broadcast=True)
