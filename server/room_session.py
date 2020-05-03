"""Inspired by https://stackoverflow.com/questions/20036520/what-is-the-purpose-of-flasks-context-stacks"""

from flask import request


def _get_room_id_from_url(url):
    # URL is smth like http://domainname.com/<room_id>/maybe/smth/here
    return url.split("/")[3]


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

    def release(self):
        room_id = get_room_id()
        self._all_rooms_data.pop(room_id, None)


room_session = RoomSession()

