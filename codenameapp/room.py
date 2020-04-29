
from flask import session, request
from flask_socketio import Namespace, emit

from codenameapp.game import Game
from codenameapp.users import User
from codenameapp import logger

class RoomNamespace(Namespace):
    def __init__(self, name, add_game_func):
        super(RoomNamespace, self).__init__(name)
        # Track ALL users
        # I don't think we actually need that (just users of one room_id)
        self.users = []
        self.add_game = add_game_func

    def on_connect(self):
        logger.debug(f"Socket {request.sid} (user {session.get('pseudo', None)}) connected!")
        logger.debug("Connected to room Namespace!")
        if "user_id" not in session:
            # There is a better way to handle errors in sockets
            raise Exception("No user_id!")

        session_id = session["user_id"]
        logger.info(f'Welcome back user {session_id} - {session["pseudo"]} !')
        new_user = User(session_id)
        # Should get room_id here (from request) then store users by room_id
        self.users.append(new_user)

    def on_disconnect(self):
        logger.debug("Disconnected from room Namespace!")
        user_id = session.get("user_id", None)
        i, user = self.get_user_by_id(user_id)
        self.users.pop(i)

    def get_user_by_id(self, user_id):
        for i, u in enumerate(self.users):
            if u.id == user_id:
                return i, u

    def on_start_game(self):
        logger.info("start game")
        logger.debug(request.__dict__)
        url = request.environ["HTTP_REFERER"]  # Access to request context
        grid_url = url.replace("room", "grid")
        room_id = url.split("/")[-2]
        game = Game(self.users, [])
        self.add_game({room_id: game})
        emit("url_redirection", {"url": grid_url}, broadcast=True)

    def on_debug_button(self):
        print("on_debug_button")
        a = request.cookies.get('user_id')
        b = request.cookies.get('pseudo')
        c = request.cookies.get('avatar-col1')
        d = request.cookies.get('avatar-col2')
        print(a, b, c, d)
