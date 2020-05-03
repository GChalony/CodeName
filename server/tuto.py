from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, Namespace, emit, join_room, leave_room, \
    close_room, rooms, disconnect, send
from uuid import uuid4

from .routes import RouteManager

class TutoNamespace(Namespace):
    def __init__(self, namespace=None, appCtx=None):
        super(TutoNamespace, self).__init__(namespace)
        self.appCtx = appCtx
        self.all_rooms = {}
        self.all_users = {}

    def on_my_event(self, message):
        update_receive_count()
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']})

    def on_my_broadcast_event(self, message):
        update_receive_count()
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']},
             broadcast=True)

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

    def on_disconnect_request(self):
        update_receive_count()
        emit('my_response',
             {'data': 'Disconnected!', 'count': session['receive_count']})
        disconnect()

    def on_my_ping(self):
        emit('my_pong')

    def on_connect(self):
        emit('my_response', {'data': f'{session.get("user_id")} Connected', 'count': 0})

    def on_disconnect(self):
        print('Client disconnected', request.sid)

### UTILS ###

def update_receive_count():
    session['receive_count'] = session.get('receive_count', 0) + 1
