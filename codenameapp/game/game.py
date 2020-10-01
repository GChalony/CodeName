import logging
from collections import Counter
from random import shuffle

import numpy as np
from flask import session

from codenameapp.frontend_config import RED
from codenameapp.utils import generate_random_words, generate_response_grid, parse_cell_code

logger = logging.getLogger(__name__)

CELLS = np.array([[f'r{r}c{c}' for c in range(5)] for r in range(5)])


class Game:
    def __init__(self, teams, spies=(0, 0)):
        self.teams = teams
        self.team_names = ["Rouge", "Bleue"]
        self.spies_idx = spies
        self.spies = (teams[0][spies[0]], teams[1][spies[1]])
        self.guessers = [[u for u in team if u not in self.spies] for team in teams]

        self.words = generate_random_words("static/ressources/words.csv")
        # 0: nothing, 1: red, 2: blue, 3: black
        self.answers = generate_response_grid()
        self.current_mask = np.zeros((5, 5))

        self.waiting_for_hint = True

        self.current_team_idx = 0

        self.guessers_enabled_list = set()

        self.current_votes = {}

    def __str__(self):
        return f"Team {self.current_team_idx} - spy {self.current_spy} is spy."

    @property
    def current_team(self):
        return self.teams[self.current_team_idx]

    @property
    def other_team_idx(self):
        return 0 if self.current_team_idx == 1 else 1

    @property
    def current_spy_idx(self):
        return self.spies_idx[self.current_team_idx]

    @property
    def current_spy(self):
        return self.spies[self.current_team_idx]

    @property
    def other_spy(self):
        return self.spies[self.other_team_idx]

    @property
    def current_team_name(self):
        return self.team_names[self.current_team_idx]

    @property
    def current_guessers(self):
        return self.guessers[self.current_team_idx]

    @property
    def other_guessers(self):
        return self.guessers[self.other_team_idx]

    @property
    def other_team_name(self):
        return self.team_names[self.other_team_idx]

    @property
    def guessers_enabled(self):
        return not self.waiting_for_hint

    @property
    def current_players(self):
        return self.current_guessers if self.guessers_enabled else [self.current_spy]

    def get_votes_counts(self):
        count = Counter(list(self.current_votes.values()))
        votes_counts = {cell: n for cell, n in count.most_common() if cell != "none"}
        return votes_counts

    def hint(self, hint, number):
        # Receive spy's hint (and do nothing with it)
        self.waiting_for_hint = False

    def vote(self, user_id, code):
        if user_id not in self.guessers_enabled_list:
            raise PermissionError(f"Votes not allowed for user {user_id}")
        logger.debug(f"User {user_id} is voting {code}")
        self.current_votes[user_id] = code

    def is_voting_done(self):
        return len(self.current_votes) == len(self.current_team) - 1

    def is_game_over(self):
        # Check black
        if self.current_mask[np.where(self.answers == 3)]:
            return True
        # Check nb blue/red left
        not_guessed_idx = np.where(1-self.current_mask)
        vals_left = self.answers[not_guessed_idx]
        n_red, n_blue = (vals_left == 1).sum(), (vals_left == 2).sum()
        return n_red == 0 or n_blue == 0

    def winner(self):
        assert self.is_game_over()
        if np.where(1-self.current_mask):
            return self.other_team_idx
        else:
            return self.current_team_idx

    def get_team_vote(self):
        vals = [v for v in self.current_votes.values() if v != "none"]
        shuffle(vals)  # Shuffle to be random in case equal counts
        c = Counter(vals).most_common(1)
        most_voted = c[0][0] if len(c) else None
        logger.debug(f"Team vote: {most_voted}")
        return most_voted

    def enable_guesser(self, user):
        self.guessers_enabled_list.add(user)

    def disable_guesser(self, user):
        logger.debug("Disabling %s from %s", user, self.guessers_enabled_list)
        self.guessers_enabled_list.remove(user)

    def end_votes(self):
        logger.debug("Ending votes")
        voted = self.get_team_vote()
        self.current_votes = {}
        logger.debug(f"End votes: {self.guessers}")
        if voted is None:
            return None, None

        r, c = parse_cell_code(voted)
        value = self.answers[r, c]
        self.current_mask[r, c] = 1

        return voted, value

    def switch_teams(self):
        self.current_team_idx = self.other_team_idx
        self.guessers_enabled_list = set()

    def is_good_answer(self, value):
        return value is not None and value == self.current_team_idx + 1


class GameState:
    """This class stores any state relative to the current game being played,
    and provides convenient properties to extract state for specific user."""

    def __init__(self, game_instance, teams):
        self.game_instance: Game = game_instance
        self.teams = teams
        self.has_started = False
        self.chat_history = []
        self.events_history = []
        self.socketio_id_from_user_id = {}
        self.game_title = None
        self.title_color = None

    def init(self):
        logger.info("Initiating game session")
        self.has_started = True
        self.game_title = f"Equipe {self.game_instance.current_team_name}"
        self.title_color = RED

    @property
    def user_id(self):
        return session["user_id"]

    @property
    def is_spy(self):
        return self.user_id in self.game_instance.spies

    @property
    def is_enabled_spy(self):
        return self.user_id == self.game_instance.current_spy \
               and self.game_instance.waiting_for_hint

    @property
    def answers(self):
        if self.is_spy:
            return self.game_instance.answers
        else:
            # Forge answers dict with -1 if values not yet discovered
            answers = {f'r{r}c{c}': -1 for r in range(5) for c in range(5)}
            for r in range(5):
                for c in range(5):
                    cell = f'r{r}c{c}'
                    answers[cell] = self.game_instance.answers[r, c]
            return answers

    @property
    def is_enabled_guesser(self):
        return self.user_id in self.game_instance.guessers_enabled_list


if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    g = Game([["a", "b", "c"], ["d", "e", "f"]])

    logger.info(g.vote("b", "r2c4"))
    logger.info(g.vote("c", "r3c0"))
    # Should end vote
    logger.info(g.vote("e", "r4c2"))
    logger.info(g.vote("f", "r4c2"))
