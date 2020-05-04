import logging
from collections import Counter
from random import shuffle

import numpy as np
from flask import session, request
from flask_socketio import Namespace, emit

from server.room_session import room_session
from server.users import User
from server.utils import generate_random_words, generate_response_grid, parse_cell_code

logger = logging.getLogger(__name__)


class Game:
    def __init__(self, teams):
        self.teams = teams
        self.len_teams = (len(teams[0]), len(teams[1]))

        self.words = generate_random_words("server/ressources/words.csv")
        self.answers = generate_response_grid()
        self.current_mask = np.zeros((5, 5))

        self.current_team = 0
        self.current_player = 0
        self.last_player = None

        self.votes = {}

    def _get_next_team(self):
        return 0 if self.current_team == 1 else 1

    def _get_next_player(self):
        next_team = self._get_next_team()
        if self.last_player is None:
            return 0
        return (self.last_player + 1) % self.len_teams[next_team]

    def vote(self, user_id, code):
        logger.debug(f"User {user_id} is voting {code}")
        if user_id not in self.teams[self.current_team]:
            raise Exception(f"Vote from wrong team: {user_id} !")
        if self.teams[self.current_team].index(user_id) == self.current_player:
            raise Exception(f"Vote from current player {user_id}!")
        self.votes[user_id] = code
        logger.debug(f"Votes: {self.votes}")
        if self.voting_done():
            voted = self.end_round()
            return voted

    def voting_done(self):
        return len(self.votes) == self.len_teams[self.current_team] - 1

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
        last_player = self.current_player
        self.current_team = (self.current_team + 1) % 2
        self.current_player = self._get_next_player()
        self.last_player = last_player

        return voted, value


class GameNamespace(Namespace):
    def on_connect(self):
        if "user_id" in session:
            logger.info(f'Welcome back user {session["pseudo"]} !')
        else:
            raise Exception("User not authenticated")

    def on_disconnect(self):
        pseudo = session.get("pseudo", None)
        logger.info(f"User {pseudo} left the game !")

    def on_chat_message(self, msg):
        logger.debug("Received : "+msg)
        emit("chat_msg", session["pseudo"] + " : " + msg, broadcast=True)

    def _get_votes_counts(self):
        votes_per_user = room_session.game.votes
        count = Counter(votes_per_user)
        return count.most_common()

    def on_vote_cell(self, code):
        user_id = "2"  # session["user_id"]  # Fake id to play
        logger.debug(f"Voting: user={user_id} cell={code}")
        logger.debug(f"Teams_ids: {room_session.game.teams}")
        res = room_session.game.vote(user_id, code)
        if res is None:  # Votes not done
            votes_counts = self._get_votes_counts()
            logger.debug(f"Votes counts: {votes_counts}")
            emit("update_votes", votes_counts)
        else:
            vote = {"cell": res[0], "value": str(res[1])}
            logger.debug(f"Switching teams: {vote}")
            emit("vote_done", vote, broadcast=True)
            # Swith current player
            result = {
                "current_player": room_session.game.current_player
            }
            emit("switch_teams", result, broadcast=True)
            pass  # Switch teams etc



if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    g = Game([["a", "b", "c"], ["d", "e", "f"]])

    logger.info(g.vote("b", "r2c4"))
    logger.info(g.vote("c", "r3c0"))
    # Should end vote
    logger.info(g.vote("e", "r4c2"))
    logger.info(g.vote("f", "r4c2"))
