import logging
import time

from flask import request, render_template, session
from flask_socketio import Namespace, join_room
from werkzeug.utils import redirect

from codenameapp.frontend_config import BLUE, RED
from codenameapp.room_session import get_room_id, emit_in_room
from codenameapp.room_session import room_session as rs
from codenameapp.utils import parse_cell_code, parse_for_emojis

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
        rs.game_title = f"Equipe {rs.game.current_team_name}"

    def load_page(self, room_id):
        if not hasattr(rs, "game"):
            logger.warning("No game in room session")
            return redirect(f"/{room_id}/room")
        if not hasattr(rs, "has_started") or not rs.has_started:
            self.init_game_session()
        user_id = session["user_id"]
        logger.info(f'Welcome back user {session["pseudo"]} !')

        is_spy = user_id in rs.game.spies
        answers = rs.game.answers if is_spy else None
        is_spy_enabled = user_id == rs.game.current_spy and not rs.game.guessers_enabled
        return render_template("grid.html",
                               toptitle=rs.game_title,
                               title_color=BLUE if rs.game.current_team_idx else RED,
                               words=rs.game.words,
                               answers=answers,
                               teams=rs.teams,
                               is_spy=is_spy,
                               is_spy_enabled=is_spy_enabled,
                               current_players=rs.game.current_players,
                               is_enabled_guesser=user_id in rs.game.guessers_enabled_list,
                               chat_history=rs.chat_history,
                               events_history=rs.events_history,
                               votes_history=rs.votes_history)

    # Socketio events handlers
    def on_connect(self):
        user_id = session["user_id"]
        if not hasattr(rs, "socketio_id_from_user_id"):
            logger.warning("No socketio_id_from_user_id -> ignoring connect event")
            return

        rs.socketio_id_from_user_id[user_id] = request.sid
        join_room(get_room_id())

        pseudo = session["pseudo"]
        self.send_new_event(f"{pseudo} a rejoint la partie")

        self.update_cell_votes(user_id)
        logger.debug(f"Socketio mapping: {rs.socketio_id_from_user_id}")

    def on_disconnect(self):
        pseudo = session["pseudo"]
        logger.info(f"User {pseudo} left the game !")
        user_id = session["user_id"]
        self.send_new_event(f"{pseudo} a quitté la partie")
        if not hasattr(rs, "socketio_id_from_user_id"):  # Avoid bug when rs reset for some reason
            logger.warning("No socketio_id_from_user_id -> ignoring disconnect event")
            return
        rs.socketio_id_from_user_id.pop(user_id)
        if len(rs.socketio_id_from_user_id) == 0:  # Remove entire game instance
            logger.info("Releasing whole game")
            rs.release()

    def on_chat_message(self, msg):
        logger.debug("Chat : " + msg)
        response = session.get("pseudo") + " : " + parse_for_emojis(msg)
        rs.chat_history.append(response)
        emit_in_room("chat_msg", response)

    def on_hint(self, hint, n):
        pseudo = session["pseudo"]
        logger.debug(f"Received hint from {pseudo}: {hint} - {n}")
        rs.game.send_hint(hint, n)
        self.change_title(f"Indice : {hint}  <span class='badge badge-{rs.game.current_team_name}'>{n}</span>",
                          color=BLUE
                if rs.game.current_team_idx else RED)
        self.send_new_event(f"Indice de {pseudo}: {hint} - {n}")
        self.enable_votes(*rs.game.current_guessers)
        self.update_current_players()

    def on_vote_cell(self, code):
        user_id = session["user_id"]
        pseudo = session["pseudo"]

        game = rs.game
        game.vote(user_id, code)

        if code == "none":
            ev = f"{pseudo} a passé"
        else:
            r, c = parse_cell_code(code)
            ev = f"{pseudo} a voté {rs.game.words[r, c]}"
        self.send_new_event(ev)
        self.disable_votes(user_id)
        if not game.is_voting_done():
            # Not everyone has voted
            self.update_cell_votes()
        else:
            # Votes are done
            self.end_votes()

    def end_votes(self):
        cell, value = rs.game.end_votes()
        if rs.game.is_game_over():
            self.game_over(rs.game.other_team_idx)
        elif cell is not None:
            # Vote cell then start votes again
            self.notify_cell_votes(cell, value)
            rs.votes_history[cell] = value
            r, c = parse_cell_code(cell)
            self.send_new_event(f"L'équipe {rs.game.current_team_name} a voté {rs.game.words[r, c]}")
            if rs.game.is_good_answer(value):
                self.enable_votes(*rs.game.current_guessers)
            else:
                # Wrong answer -> switch teams
                self.send_new_event("Raté !")
                self.switch_teams()
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
                emit_in_room("update_votes", votes_counts,
                             room=rs.socketio_id_from_user_id[user_id])

    def switch_teams(self):
        logger.debug(f"Switching teams")
        rs.game.switch_teams()
        self.change_title(f"Equipe {rs.game.current_team_name}", color=BLUE if
                rs.game.current_team_idx else RED)
        self.update_current_players()
        self.enable_controls()

    def notify_cell_votes(self, cell, value):
        vote = {"cell": cell, "value": str(value)}
        emit_in_room("vote_done", vote)

    def change_title(self, new_title, color="white"):
        rs.game_title = new_title
        emit_in_room('change_title', {"title": new_title, "color": color})

    def enable_controls(self):
        emit_in_room("enable_controls", room=rs.socketio_id_from_user_id[rs.game.current_spy])

    def update_current_players(self):
        logger.debug(f"Updating current players: {rs.game.current_players}")
        emit_in_room("change_current_player", rs.game.current_players)

    def enable_votes(self, *player_ids):
        logger.debug(f"Enabling votes: {rs.game.guessers_enabled_list}")
        if not rs.game.guessers_enabled:
            raise PermissionError("Guessers not enabled!")

        logger.debug(f"Enabling votes for users ids {player_ids}")
        for player_id in player_ids:
            emit_in_room("enable_vote", room=rs.socketio_id_from_user_id[player_id])

    def disable_votes(self, *player_ids):
        logger.debug(f"Disabling votes for users ids {player_ids}")
        for player_id in player_ids:
            emit_in_room("disable_vote", room=rs.socketio_id_from_user_id[player_id])

    def send_new_event(self, event_msg):
        logger.debug(f"Sending new event {event_msg}")
        rs.events_history.append(event_msg)
        emit_in_room("add_event", event_msg)

    def _get_remaining_cells(self):
        cells = list(rs.game.votes.values())  # Cells currently voted for
        done_cells = list(rs.votes_history.keys())  # Cell already seen by everyone
        all_cells = [f'r{r}c{c}' for r in range(5) for c in range(5)]  # All possible cells
        cells += [cell for cell in all_cells if cell not in cells and cell not in done_cells]
        return cells

    def game_over(self, winners):
        logger.info("GAME OVER")
        self.change_title(f"L'équipe {rs.game.team_names[winners]} a gagné !")

        emit_in_room('change_controls',
                     render_template("_gameover_controls.html", room_id=get_room_id()))
        del rs.teams  # Remove teams so they appear empty when redirected to room
        # Get remaining cells values
        left_cells = self._get_remaining_cells()
        for cell in left_cells:
            value = rs.game.answers[parse_cell_code(cell)]
            self.notify_cell_votes(cell, value)
            time.sleep(1)
