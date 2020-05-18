import logging
import time

from flask import request, render_template, flash, url_for
from flask_socketio import Namespace, join_room

from server.room_session import room_session as rs, get_room_id, emit_in_room
from server.utils import parse_cell_code

logger = logging.getLogger(__name__)


class GameManager(Namespace):
    # Routes
    def init_routes(self, app):
        app.add_url_rule('/<room_id>/grid', view_func=self.load_page)

    def init_game_session(self):
        logger.info("Initiating game session")
        rs.has_started = True
        rs.chat_history = []
        rs.events_history = []
        rs.votes_history = {}
        rs.socketio_id_from_user_id = {}
        rs.votes_enabled = []
        rs.game_title = f"Equipe {rs.game.current_team_name}"

    def load_page(self, room_id):
        if not (hasattr(rs, "has_started") and rs.has_started):
            self.init_game_session()
        user_id = request.cookies["user_id"]
        answers, is_spy = None, False
        if user_id in rs.game.spies:
            answers = rs.game.answers
            is_spy = True
        return render_template("grid.html",
                               title=rs.game_title,
                               title_color="#0af" if rs.game.current_team_idx else "#ff5300",
                               words=rs.game.words,
                               teams=rs.teams,
                               spy_enabled=user_id == rs.game.current_spy,
                               is_spy=is_spy,
                               current_spy=rs.game.current_spy,
                               answers=answers,
                               chat_history=rs.chat_history,
                               events_history=rs.events_history,
                               votes_history=rs.votes_history)

    # Socketio events handles
    def on_connect(self):
        if "user_id" not in request.cookies:
            raise Exception("User not authenticated")
        user_id = request.cookies["user_id"]
        logger.info(f'Welcome back user {request.cookies["pseudo"]} !')
        rs.socketio_id_from_user_id[user_id] = request.sid
        join_room(get_room_id())

        pseudo = request.cookies["pseudo"]
        self.send_new_event(f"{pseudo} a rejoint la partie")

        if user_id in rs.votes_enabled:
            self.enable_votes(user_id)
        self.update_cell_votes(user_id)

    def on_disconnect(self):
        user_id = request.cookies["user_id"]
        pseudo = request.cookies["pseudo"]
        self.send_new_event(f"{pseudo} a quitté la partie")
        rs.socketio_id_from_user_id.pop(user_id)
        pseudo = request.cookies.get("pseudo", None)
        logger.info(f"User {pseudo} left the game !")

    def on_chat_message(self, msg):
        logger.debug("Chat : "+msg)
        response = request.cookies.get("pseudo") + " : " + msg
        rs.chat_history.append(response)
        emit_in_room("chat_msg", response)

    def on_hint(self, hint, n):
        pseudo = request.cookies["pseudo"]
        logger.debug(f"Received hint from {pseudo}: {hint} - {n}")
        self.change_title(f"Indice : {hint} - {n}")
        self.send_new_event(f"Indice de {pseudo}: {hint} - {n}")
        self.enable_votes(*rs.game.current_guessers)

    def on_vote_cell(self, code):
        user_id = request.cookies["user_id"]  # session["user_id"]  # TODO change back in production
        game = rs.game
        if (user_id not in game.current_guessers) and (user_id in rs.votes_enabled):
            raise PermissionError(f"Vote not allowed from user {user_id}")
        pseudo = request.cookies["pseudo"]
        if code == "none":
            ev = f"{pseudo} a passé"
        else:
            r, c = parse_cell_code(code)
            ev = f"{pseudo} a voté {rs.game.words[r, c]}"
        self.send_new_event(ev)
        game.vote(user_id, code)
        self.disable_votes(user_id)
        if not game.is_voting_done():
            # Not everyone has voted
            self.update_cell_votes()
        else:
            # Votes are done
            cell, value = game.end_votes()
            if game.is_game_over():
                self.game_over(rs.game.current_team_idx)
            elif cell is not None:
                self.notify_cell_votes(cell, value)
                rs.votes_history[cell] = value
                r, c = parse_cell_code(cell)
                self.send_new_event(f"L'équipe {game.current_team_name} a voté {game.words[r, c]}")
                self.enable_votes(*rs.game.current_guessers)
            else:
                # Everybody passed -> change teams
                self.send_new_event(f"Team {rs.game.current_team_name} a passé")
                self.switch_teams()

    def update_cell_votes(self, user_id=None):
        votes_counts = rs.game.get_votes_counts()
        logger.debug(f"Votes counts: {votes_counts}")
        if len(votes_counts):  # Check that contains actual values and not just pass
            if user_id is None:
                emit_in_room("update_votes", votes_counts)
            else:
                emit_in_room("update_votes", votes_counts, room=rs.socketio_id_from_user_id[user_id])

    def notify_cell_votes(self, cell, value):
        vote = {"cell": cell, "value": str(value)}
        emit_in_room("vote_done", vote)

    def change_title(self, new_title, color="white"):
        rs.game_title = new_title
        emit_in_room('change_title', {"title": new_title, "color": color})

    def enable_controls(self):
        emit_in_room("enable_controls", room=rs.socketio_id_from_user_id[rs.game.current_spy])

    def change_current_player(self, new_player_id):
        emit_in_room("change_current_player", new_player_id)

    def enable_votes(self, *player_ids):
        logger.debug(f"Enabling votes for users ids {player_ids}")
        for player_id in player_ids:
            rs.votes_enabled.append(player_id)
            emit_in_room("enable_vote", room=rs.socketio_id_from_user_id[player_id])

    def disable_votes(self, *player_ids):
        logger.debug(f"Disabling votes for users ids {player_ids}")
        for player_id in player_ids:
            rs.votes_enabled.remove(player_id)
            emit_in_room("disable_vote", room=rs.socketio_id_from_user_id[player_id])

    def send_new_event(self, event_msg):
        logger.debug(f"Sending new event {event_msg}")
        rs.events_history.append(event_msg)
        emit_in_room("add_event", event_msg)

    def switch_teams(self):
        logger.debug(f"Switching teams")
        rs.game.switch_teams()
        self.change_title(f"Equipe {rs.game.current_team_name}", color="#0af"
            if rs.game.current_team_idx else "#ff5300")
        self.change_current_player(rs.game.current_spy)
        self.enable_votes(*rs.game.current_guessers)
        self.enable_controls()

    def _get_remaining_cells(self):
        cells = list(rs.game.votes.values())  # Cells currently voted for
        done_cells = list(rs.votes_history.keys())  # Cell already seen by everyone
        all_cells = [f'r{r}c{c}' for r in range(5) for c in range(5)]  # All possible cells
        cells += [cell for cell in all_cells if cell not in cells and cell not in done_cells]
        logger.debug(cells)
        logger.debug(done_cells)
        return cells

    def game_over(self, winners):
        logger.info("GAME OVER")
        self.change_title(f"L'équipe {rs.game.team_names[winners]} a gagné !")

        emit_in_room('change_controls',
                     render_template("_gameover_controls.html", room_id=get_room_id()))
        # Get remaining cells values
        left_cells = self._get_remaining_cells()
        for cell in left_cells:
            value = rs.game.answers[parse_cell_code(cell)]
            self.notify_cell_votes(cell, value)
            time.sleep(2)
