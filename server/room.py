
from flask import session, request
from flask_socketio import Namespace, emit
import logging

from server.game import Game
from server.users import User

logger = logging.getLogger(__name__)

class RoomNamespace(Namespace):
    def __init__(self, name, add_game_func):
        super(RoomNamespace, self).__init__(name)
        # Track ALL users
        # I don't think we actually need that (just users of one room_id)
        self.users = []
        self.add_game = add_game_func

    def on_connect(self):
        # Have access to session here
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



    def on_join(self, message):
        user_id = session.get("user_id", uuid4().hex)
        session["user_id"] = user_id
        new_room = message['room']
        if user_id not in self.all_users:
            self.all_users[user_id] = [new_room]
        else:
            self.all_users[user_id].append(new_room)

        if new_room not in self.all_rooms:
            self.all_rooms[new_room] = [user_id]
        elif user_id not in self.all_rooms[new_room]:
            self.all_rooms[new_room].append(user_id)

        print("new_room", new_room)
        print("self.all_rooms", self.all_rooms)
        join_room(new_room)
        update_receive_count()
        emit('my_response',
             {'data': 'In rooms: ' + ', '.join(rooms()),
              'count': session['receive_count']})
        # send('Toto has entered the room.', room=new_room)

    def on_leave(self, message):
        user_id = session.get("user_id")
        new_room = message['room']
        if new_room in self.all_users[user_id]:
            self.all_users[user_id].remove(new_room)
        print("on leave, self.all_users=", self.all_users)
        leave_room(message['room'], user_id)
        update_receive_count()
        emit('my_response',
             {'data': 'In rooms: ' + ', '.join(rooms()),
              'count': session['receive_count']})

    def on_close_room(self, message):
        room = message['room']
        del self.all_rooms[room]
        print("self.all_rooms2", self.all_rooms)
        update_receive_count()
        emit('my_response', {'data': 'Room ' + room + ' is closing.',
                             'count': session['receive_count']},
             room=room)
        close_room(room)

    def on_my_room_event(self, message):
        update_receive_count()
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']},
             room=message['room'])


    def on_debug_button(self):
        print("on_debug_button")
        a = request.cookies.get('user_id')
        b = request.cookies.get('pseudo')
        c = request.cookies.get('avatar-col1')
        d = request.cookies.get('avatar-col2')
        print(a, b, c, d)

