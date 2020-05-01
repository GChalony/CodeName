from flask import Flask, render_template, request, url_for, redirect, session
from flask_session import Session
from flask_socketio import SocketIO

from codenameapp.game import Game
from codenameapp.game import Game, GameNamespace
from codenameapp.room import RoomNamespace

# Import Flask app
from codenameapp import app

### SESSION ###
Session(app)  # Instanciate session to store data to filesystem
socketio = SocketIO(app, manage_session=False)  # Let flask-session handle sessions

g = Game(["greg", "clem", "sol", "axel"], [["greg", "clem"], ["sol", "axel"]])
games = {"0": g}
temp_default_teams = [["Greg", "Sol"], ["Axel", "Clem"]]

### ADD SOCKETIO EVENT LISTENERS ###
socketio.on_namespace(RoomNamespace("/room", games.update))
socketio.on_namespace(GameNamespace("/game"))

if __name__ == "__main__":
    socketio.run(app, debug=True)
