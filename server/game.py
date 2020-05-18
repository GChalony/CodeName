import logging
from collections import Counter
from random import shuffle

import numpy as np

from server.utils import generate_random_words, generate_response_grid, parse_cell_code

logger = logging.getLogger(__name__)


class Game:
    def __init__(self, teams, spies=(0, 0)):
        self.teams = teams
        self.team_names = ["Rouge", "Bleue"]
        self.spies_idx = spies
        self.spies = (teams[0][spies[0]], teams[1][spies[1]])
        self.guessers = [[u for u in team if u not in self.spies] for team in teams]

        self.words = generate_random_words("server/ressources/words.csv")
        # 0: nothing, 1: red, 2: blue, 3: black
        self.answers = generate_response_grid()
        self.current_mask = np.zeros((5, 5))

        self.current_team_idx = 0

        self.votes = {}

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

    def get_votes_counts(self):
        count = Counter(list(self.votes.values()))
        votes_counts = {cell: n for cell, n in count.most_common() if cell != "none"}
        return votes_counts

    def vote(self, user_id, code):
        logger.debug(f"User {user_id} is voting {code}")
        if user_id not in self.current_team:
            raise PermissionError(f"Vote from wrong team: {user_id} !")
        if user_id == self.current_spy:
            raise PermissionError(f"Vote from current player {user_id}!")
        self.votes[user_id] = code
        logger.debug(f"Votes: {self.votes}")

    def is_voting_done(self):
        return len(self.votes) == len(self.current_team) - 1

    def is_game_over(self):
        # Check black
        if self.current_mask[np.where(self.answers == 3)]:
            return True
        # Check nb blue/red left
        not_guessed_idx = np.where(1-self.current_mask)
        vals_left = self.answers[not_guessed_idx]
        n_red, n_blue = (vals_left == 1).sum(), (vals_left == 2).sum()
        return n_red == 0 or n_blue == 0

    def get_team_vote(self):
        vals = [v for v in self.votes.values() if v != "none"]
        shuffle(vals)  # Shuffle to be random in case equal counts
        c = Counter(vals).most_common(1)
        most_voted = c[0][0] if len(c) else None
        logger.debug(f"Team vote: {most_voted}")
        return most_voted

    def end_votes(self):
        logger.debug("Ending votes")
        voted = self.get_team_vote()
        self.votes = {}

        if voted is None:
            return None, None

        r, c = parse_cell_code(voted)
        value = self.answers[r, c]
        self.current_mask[r, c] = 1
        return voted, value

    def switch_teams(self):
        self.current_team_idx = self.other_team_idx


if __name__ == "__main__":
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    g = Game([["a", "b", "c"], ["d", "e", "f"]])

    logger.info(g.vote("b", "r2c4"))
    logger.info(g.vote("c", "r3c0"))
    # Should end vote
    logger.info(g.vote("e", "r4c2"))
    logger.info(g.vote("f", "r4c2"))
