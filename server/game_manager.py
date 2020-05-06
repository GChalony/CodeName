import logging

from flask import request, render_template
from flask_socketio import Namespace, emit

from server.room_session import room_session as rs
from server.utils import parse_cell_code

logger = logging.getLogger(__name__)


class GameManager(Namespace):
    # Routes
    def init_routes(self, app):
        app.add_url_rule('/<room_id>/grid', view_func=self.load_page)

    def load_page(self, room_id):
        # TODO adapt to reload
        user_id = request.cookies["user_id"]
        answers, is_spy = None, False
        if user_id in rs.game.spies:
            answers = rs.game.answers
            is_spy = True
        return render_template("grid.html",
                               title=f"Equipe {rs.game.current_team_name}",
                               words=rs.game.words,
                               teams=rs.teams,
                               spy_enabled=user_id == rs.game.current_spy,
                               is_spy=is_spy,
                               answers=answers)

    # Socketio events handles
    def on_connect(self):
        if "user_id" not in request.cookies:
            raise Exception("User not authenticated")
        user_id = request.cookies["user_id"]
        logger.info(f'Welcome back user {request.cookies["pseudo"]} !')
        logger.info(f"It's {rs.game.current_team_name}'s turn")
        # Store mapping of user_id <-> socketio id  TODO rid
        if not hasattr(rs, "socketio_id_to_user_id"):
            rs.socketio_id_to_user_id = {}
        rs.socketio_id_to_user_id[user_id] = request.sid

        pseudo = request.cookies["pseudo"]
        self.send_new_event(f"{pseudo} a rejoint la partie")


    def on_disconnect(self):
        pseudo = request.cookies.get("pseudo", None)
        logger.info(f"User {pseudo} left the game !")

    def on_chat_message(self, msg):
        logger.debug("Chat : "+msg)
        emit("chat_msg", request.cookies.get("pseudo") + " : " + msg, broadcast=True)

    def on_hint(self, hint, n):
        pseudo = request.cookies["pseudo"]
        logger.debug(f"Received hint from {pseudo}: {hint} - {n}")
        self.change_title(f"Indice : {hint} - {n}")
        self.send_new_event(f"Indice de {pseudo}: {hint} - {n}")
        self.enable_votes(*rs.game.current_guessers)

    def on_vote_cell(self, code):
        user_id = request.cookies["user_id"]  # session["user_id"]  # TODO change back in production
        game = rs.game
        try:
            res = game.vote(user_id, code)
            if res is None:
                # Votes not done
                self.update_cell_votes()
            else:
                # Votes are done, change teams etc
                cell, value = res
                self.notify_cell_votes(cell, value)
                r, c = parse_cell_code(cell)
                self.send_new_event(f"Team {game.current_team_name} voted {game.words[r, c]}")
                self.switch_teams(game.current_spy)
        except PermissionError as e:
            logger.debug(game)
            logger.error(e)

    def update_cell_votes(self):
        votes_counts = rs.game.get_votes_counts()
        logger.debug(f"Votes counts: {votes_counts}")
        emit("update_votes", votes_counts)

    def notify_cell_votes(self, cell, value):
        vote = {"cell": cell, "value": str(value)}
        emit("vote_done", vote, broadcast=True)

    def change_title(self, new_title):
        emit('change_title', new_title, broadcast=True)

    def toggle_controls(self):
        emit("toggle_controls", room=rs.socketio_id_to_user_id[rs.game.current_spy])

    def change_current_player(self, new_player_id):
        emit("change_current_player", new_player_id, broadcast=True)

    def enable_votes(self, *player_ids):
        logger.debug(f"Enabling votes for users ids {player_ids}")
        for player_id in player_ids:
            emit("enable_vote", room=rs.socketio_id_to_user_id[player_id])

    def disable_votes(self, player_ids):
        logger.debug(f"Disabling votes for users ids {player_ids}")
        for player_id in player_ids:
            emit("disable_vote", room=rs.socketio_id_to_user_id[player_id])

    def send_new_event(self, event_msg):
        logger.debug(f"Sending new event {event_msg}")
        emit("add_event", event_msg, broadcast=True)

    def switch_teams(self, spy_id):
        logger.debug(f"Switching teams")
        self.change_title(f"Equipe {rs.game.current_team_name}")
        self.change_current_player(spy_id)
        self.disable_votes(rs.game.teams[(rs.game.current_team_idx+1) % 2])
        self.enable_votes(*rs.game.current_guessers)
        self.toggle_controls()
