from uuid import uuid4

from flask import session, request
from flask_socketio import Namespace, emit

from codenameapp.game import Game
from codenameapp.users import User


class RoomNamespace(Namespace):
    def __init__(self, name, add_game_func):
        super(RoomNamespace, self).__init__(name)
        # Track ALL users
        # I don't think we actually need that
        self.users = []
        self.add_game = add_game_func

    def on_connect(self):
        print("Connect!")
        if "user_id" in session:
            session_id = session["user_id"]
            print(f'Welcome back user {session_id} - {session["pseudo"]} !')
        else:
            raise Exception("No user_id!")
        new_user = User(session_id)
        self.users.append(new_user)

    def on_disconnect(self):
        print("Disconnected!")
        user_id = session.get("user_id", None)
        print(f"Disconnecting {user_id} - {session['pseudo']} ")
        i, user = self.get_user_by_id(user_id)
        self.users.pop(i)

    def get_user_by_id(self, user_id):
        for i, u in enumerate(self.users):
            if u.id == user_id:
                return i, u

    def on_start_game(self):
        print("start game")
        print(request.__dict__)
        url = request.environ["HTTP_REFERER"]
        grid_url = url.replace("room", "grid")
        room_id = url.split("/")[-2]
        game = Game(self.users, [])
        self.add_game({room_id: game})
        print("grid_url", grid_url)
        emit("url_redirection", {"url": grid_url}, broadcast=True)

    def on_debug_button(self):
        print("on_debug_button")
        a = request.cookies.get('user_id')
        b = request.cookies.get('pseudo')
        c = request.cookies.get('avatar-col1')
        d = request.cookies.get('avatar-col2')
        print(a, b, c, d)

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
