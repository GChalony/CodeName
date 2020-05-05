import logging
from collections import Counter
from random import shuffle

import numpy as np
from flask import request
from flask_socketio import Namespace, emit

from server.room_session import room_session
from server.utils import generate_random_words, generate_response_grid, parse_cell_code

logger = logging.getLogger(__name__)


class Game:
    def __init__(self, teams):
        self.teams = teams
        self.len_teams = (len(teams[0]), len(teams[1]))

        self.words = generate_random_words("server/ressources/words.csv")
        self.answers = generate_response_grid()
        self.current_mask = np.zeros((5, 5))

        self.current_team_idx = 0
        self.current_player_idx = 0
        self.last_player_idx = None

        self.votes = {}

    def __str__(self):
        return f"Team {self.current_team_idx} - player {self.current_player} is spy.\n" \
                f"Last player={self.last_player_idx} and votes={self.votes}"

    @property
    def current_team(self):
        return self.teams[self.current_team_idx]

    @property
    def current_player(self):
        return self.current_team[self.current_player_idx]

    @property
    def current_team_name(self):
        return ["Rouge", "Bleu"][self.current_team_idx]

    @property
    def current_guessers(self):
        return [u for u in self.current_team if u != self.current_player]

    def _get_next_team(self):
        return 0 if self.current_team_idx == 1 else 1

    def _get_next_player(self):
        next_team = self._get_next_team()
        if self.last_player_idx is None:
            return 0
        return (self.last_player_idx + 1) % self.len_teams[next_team]

    def vote(self, user_id, code):
        logger.debug(f"User {user_id} is voting {code}")
        if user_id not in self.current_team:
            raise PermissionError(f"Vote from wrong team: {user_id} !")
        if self.current_player == user_id:
            raise PermissionError(f"Vote from current player {user_id}!")
        self.votes[user_id] = code
        logger.debug(f"Votes: {self.votes}")
        if self.voting_done():
            voted = self.end_round()
            return voted

    def voting_done(self):
        return len(self.votes) == self.len_teams[self.current_team_idx] - 1

    def get_team_vote(self):
        vals = list(self.votes.values())
        shuffle(vals)  # Shuffle to be random in case equal counts
        c = Counter(vals)
        most_voted = c.most_common(1)[0][0]
        logger.debug(f"Team vote: {most_voted}")
        return most_voted

    def end_round(self):
        logger.debug("Ending round")
        voted = self.get_team_vote()
        r, c = parse_cell_code(voted)
        value = self.answers[r, c]
        self.votes = {}

        self.current_mask[r, c] = 1

        # Switch teams
        last_player = self.current_player_idx
        self.current_team_idx = (self.current_team_idx + 1) % 2
        self.current_player_idx = self._get_next_player()
        self.last_player_idx = last_player

        return voted, value


class GameNamespace(Namespace):
    # TODO toggle controls according to user_id
    def on_connect(self):
        logger.debug(str(room_session.game))
        if "user_id" not in request.cookies:
            raise Exception("User not authenticated")
        user_id = request.cookies["user_id"]
        logger.info(f'Welcome back user {request.cookies["pseudo"]} !')
        # Store mapping of user_id <-> socketio id
        if not hasattr(room_session, "socketio_id_to_user_id"):
            room_session.socketio_id_to_user_id = {}
        room_session.socketio_id_to_user_id[user_id] = request.sid
        logger.debug(room_session.socketio_id_to_user_id)
        if user_id in room_session.game.current_guessers:
            logger.debug(f"Enabling votes for user {user_id}")
            emit("enable_vote")

    def on_disconnect(self):
        pseudo = request.cookies.get("pseudo", None)
        logger.info(f"User {pseudo} left the game !")

    def on_chat_message(self, msg):
        logger.debug("Received : "+msg)
        emit("chat_msg", request.cookies.get("pseudo") + " : " + msg, broadcast=True)

    def _get_votes_counts(self):
        votes_per_user = room_session.game.votes
        count = Counter(votes_per_user)
        return count.most_common()

    def on_vote_cell(self, code):
        user_id = request.cookies["user_id"]  # session["user_id"]  # TODO change back in production
        game = room_session.game
        previous_player_id = game.current_player
        try:
            logger.debug(f"Current state: {game}")
            res = game.vote(user_id, code)
            if res is None:  # Votes not done
                votes_counts = self._get_votes_counts()
                logger.debug(f"Votes counts: {votes_counts}")
                emit("update_votes", votes_counts)
            else:
                vote = {"cell": res[0], "value": str(res[1])}
                logger.debug(f"Switching teams: {vote}")
                emit("vote_done", vote, broadcast=True)
                r, c = parse_cell_code(vote["cell"])
                emit("add_event", f"L'equipe {game.current_team_name} a voté "
                                  f"{game.words[r, c]}", broadcast=True)
                emit('change_title', f"Equipe {game.current_team_name}", broadcast=True)
                result = {
                    "current_player_id": game.current_player
                }
                emit("switch_teams", result, broadcast=True)
                emit("toggle_controls", room=room_session.socketio_id_to_user_id[previous_player_id])
                emit("toggle_controls", room=room_session.socketio_id_to_user_id[game.current_player])

        except PermissionError as e:
            logger.debug(game)
            logger.error(e)


if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    g = Game([["a", "b", "c"], ["d", "e", "f"]])

    logger.info(g.vote("b", "r2c4"))
    logger.info(g.vote("c", "r3c0"))
    # Should end vote
    logger.info(g.vote("e", "r4c2"))
    logger.info(g.vote("f", "r4c2"))
