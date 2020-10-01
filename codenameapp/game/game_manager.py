import logging
import time
from functools import wraps

from flask import request, render_template, session
from flask_socketio import Namespace, join_room
from werkzeug.utils import redirect

from codenameapp.frontend_config import BLUE, RED
from codenameapp.room_session import get_room_id, emit_in_room
from codenameapp.room_session import room_session as rs
from codenameapp.utils import parse_cell_code, parse_for_emojis

logger = logging.getLogger(__name__)


def check_game_state(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not hasattr(rs, "game_state"):
            logger.warning("No GameState found -> ignoring connect event")
            return
        return f(*args, **kwargs)
    return wrapped


class GameManager(Namespace):
    # Routes
    def init_routes(self, app):
        app.add_url_rule('/<room_id>/grid', view_func=self.load_page)

    def load_page(self, room_id):
        if not hasattr(rs, "game"):
            logger.warning("No game in room session")
            return redirect(f"/{room_id}/room")
        if not rs.game_state.has_started:
            rs.game_state.init()
        logger.info(f'Welcome back user {session["pseudo"]} !')
        logger.debug("User %s - %s just loaded the page", session["pseudo"], session["user_id"])
        logger.debug("His state: %s, %s, %s, %s", rs.game_state.__dict__, rs.game_state.user_id, rs.game_state.is_spy,
                     rs.game_state.is_enabled_spy)
        return render_template("grid.html",
                               game_state=rs.game_state,
                               words=rs.game_state.game_instance.words,
                               )

    @check_game_state
    def on_connect(self):
        user_id = session["user_id"]

        rs.game_state.socketio_id_from_user_id[user_id] = request.sid
        join_room(get_room_id())

        pseudo = session["pseudo"]
        self.notify_new_event(f"{pseudo} a rejoint la partie")
        logger.debug(f"Socketio mapping: {rs.game_state.socketio_id_from_user_id}")
        # TODO: send state to sync

    @check_game_state
    def on_disconnect(self):
        pseudo = session["pseudo"]
        logger.info(f"User {pseudo} left the game !")
        user_id = session["user_id"]

        rs.game_state.socketio_id_from_user_id.pop(user_id)
        self.notify_new_event(f"{pseudo} a quitté la partie")

        if len(rs.game_state.socketio_id_from_user_id) == 0:  # Remove entire game instance
            logger.info("Releasing whole game")
            rs.release()

    def on_chat_message(self, msg):
        logger.debug("Chat : " + msg)
        response = session.get("pseudo") + " : " + parse_for_emojis(msg)
        rs.game_state.chat_history.append(response)
        emit_in_room("chat_msg", response)

    def on_hint(self, hint, n):
        pseudo = session["pseudo"]
        logger.debug(f"Received hint from {pseudo}: {hint} - {n}")
        rs.game.hint(hint, n)
        rs.game_state.waiting_for_hint = False
        self.notify_hint(hint, n)

    def notify_hint(self, hint, n):
        pseudo = session["pseudo"]
        title = f"Indice : {hint}  <span class='badge badge-{rs.game.current_team_name}'>{n}</span>"
        self.notify_change_title(title, color=BLUE if rs.game.current_team_idx else RED)
        self.notify_new_event(f"Indice de {pseudo}: {hint} - {n}")
        self.notify_enable_votes(*rs.game.current_guessers)
        self.notify_update_current_players()

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

        self.notify_disable_votes(user_id)
        self.notify_new_event(ev)
        if not game.is_voting_done():
            # Not everyone has voted
            self.notify_update_cell_votes()
        else:
            # Votes are done
            self.end_votes()

    def notify_update_cell_votes(self):
        votes_counts = rs.game.get_votes_counts()
        logger.debug(f"Votes counts: {votes_counts}")
        if len(votes_counts):  # Check that contains actual values and not just pass
            emit_in_room("update_votes", votes_counts)

    def end_votes(self):
        # 3 possibilities
        # - right vote -> keep going
        # - wrong vote -> switch teams
        # - game over (either won or lost)
        cell, value = rs.game.end_votes()
        if cell is None:
            self.notify_new_event(f"L'équipe {rs.game.current_team_name} a passé")
        else:
            self.notify_cell_voted(cell, value)
            r, c = parse_cell_code(cell)
            self.notify_new_event(f"L'équipe {rs.game.current_team_name} a voté {rs.game.words[r, c]}")
        if not rs.game.is_game_over():
            if rs.game.is_good_answer(value):
                # Vote cell then start votes again
                self.notify_enable_votes(*rs.game.current_guessers)
            else:
                # Wrong answer
                if cell is None:  # Everybody passed
                    ev = f"Team {rs.game.current_team_name} a passé"
                else:
                    ev = "Raté !"
                    self.notify_new_event(ev)
                    self.switch_teams()
        else:
            self.game_over(rs.game.winner())

    def notify_cell_voted(self, cell, value):
        vote = {"cell": cell, "value": str(value)}
        emit_in_room("vote_done", vote)

    def switch_teams(self):
        logger.debug(f"Switching teams")
        rs.game.switch_teams()
        rs.game_state.waiting_for_hint = True
        title = f"Equipe {rs.game.current_team_name}"
        self.notify_change_title(title, color=BLUE if rs.game.current_team_idx else RED)
        self.notify_update_current_players()
        self.notify_enable_controls()

    def notify_change_title(self, new_title, color="white"):
        rs.game_title = new_title
        rs.title_color = color
        emit_in_room('change_title', {"title": new_title, "color": color})

    def notify_enable_controls(self):
        emit_in_room("enable_controls", room=rs.game_state.socketio_id_from_user_id[rs.game.current_spy])

    def notify_update_current_players(self):
        logger.debug(f"Updating current players: {rs.game.current_players}")
        emit_in_room("change_current_player", rs.game.current_players)

    def notify_enable_votes(self, *player_ids):
        logger.debug(f"Enabling votes for users ids {player_ids}")
        for player_id in player_ids:
            rs.game.enable_guesser(player_id)
            emit_in_room("enable_vote", room=rs.game_state.socketio_id_from_user_id[player_id])

    def notify_disable_votes(self, *player_ids):
        logger.debug(f"Disabling votes for users ids {player_ids}")
        for player_id in player_ids:
            rs.game.disable_guesser(player_id)
            emit_in_room("disable_vote", room=rs.game_state.socketio_id_from_user_id[player_id])

    def notify_new_event(self, event_msg):
        logger.debug(f"Sending new event {event_msg}")
        rs.game_state.events_history.append(event_msg)
        emit_in_room("add_event", event_msg)

    def _get_remaining_cells(self):
        cells = list(rs.game.current_votes.values())  # Cells currently voted for
        done_cells = list(rs.votes_history.keys())  # Cell already seen by everyone
        all_cells = [f'r{r}c{c}' for r in range(5) for c in range(5)]  # All possible cells
        cells += [cell for cell in all_cells if cell not in cells and cell not in done_cells]
        return cells

    def game_over(self, winners):
        logger.info("GAME OVER")
        self.notify_change_title(f"L'équipe {rs.game.team_names[winners]} a gagné !")

        emit_in_room('change_controls',
                     render_template("_gameover_controls.html", room_id=get_room_id()))
        del rs.teams  # Remove teams so they appear empty when redirected to room
        # Get remaining cells values
        left_cells = self._get_remaining_cells()
        for cell in left_cells:
            value = rs.game.answers[parse_cell_code(cell)]
            self.notify_cell_voted(cell, value)
            time.sleep(1)
