"""Inspired by https://stackoverflow.com/questions/20036520/what-is-the-purpose-of-flasks-context-stacks"""

from flask import request
from flask_socketio import emit


def _get_room_id_from_url(url):
    # URL is smth like http://domainname.com/<room_id>/maybe/smth/here
    try:
        room_id = url.split("/")[3]
    except IndexError as e:
        raise RuntimeError(f"Working outside of room context: {e}")
    if not len(room_id) == 32:  # UUID is exactly 32 bytes
        raise RuntimeError("Working outside of room context")
    return room_id


def get_room_id():
    url = request.url
    if "socket.io" in url:
        # Socket context
        url = request.environ["HTTP_REFERER"]
    room_id = _get_room_id_from_url(url)
    return room_id


class RoomSession:
    def __init__(self):
        self._all_rooms_data = {}

    def __getattr__(self, name):
        room_id = get_room_id()
        # Create room namespace if didnt exist
        context_data = self._all_rooms_data.setdefault(room_id, {})
        try:
            return context_data[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name == "_all_rooms_data":
            super().__setattr__(name, value)
        else:
            room_id = get_room_id()
            # Create room namespace if didnt exist
            context_data = self._all_rooms_data.setdefault(room_id, {})
            context_data[name] = value

    def __delattr__(self, item):
        room_id = get_room_id()
        del self._all_rooms_data[room_id][item]

    def release(self):
        room_id = get_room_id()
        self._all_rooms_data.pop(room_id, None)


room_session = RoomSession()


def emit_in_room(*args, **kwargs):
    """If room arg is not provided, emits a socket msg to all sockets connected to the
    current room.

    Otherwise just calls flask_socketio.emit()."""
    room = kwargs.pop("room", get_room_id())
    emit(*args, room=room, **kwargs)
