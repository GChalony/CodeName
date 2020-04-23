import numpy as np

from app.utils import generate_random_words, generate_response_grid, parse_cell_code


class Game:
    def __init__(self, players, teams):
        self.players = players
        self.teams = teams

        self.words = generate_random_words("../ressources/words.csv")
        self.answers = generate_response_grid()
        self.current_mask = np.zeros((5, 5))

        self.current_team = 0
        self.current_player = 0
        self.last_players = [None, None]
        self.last_cell_try = None  # Could cause trouble

    def _get_next_player(self):
        next_team = (self.current_team + 1) % 2
        if self.last_players[next_team] is None:
            return 0
        return (self.last_players[next_team] + 1) % len(self.teams[next_team])

    def try_cell(self, code):
        r, c = parse_cell_code(code)
        if not self.current_mask[r, c]:
            self.current_mask[r, c] = 1
            val = self.answers[r, c]
            self.last_cell_try = code
            return val
        else:
            raise Exception("Cell already tried!")

    def end_round(self):
        self.last_players[self.current_team] = self.current_player

        self.current_team = (self.current_team + 1) % 2
        self.current_player = self._get_next_player()


if __name__ == "__main__":
    g = Game(["a", "b", "c", "d", "e", "f"], [["a", "b", "c"], ["d", "e", "f"]])
    v = g.try_cell("r1c1")
    print(v)
    print(g.current_team, g.current_player, g.current_mask)
    g.end_round()
    print(g.current_team, g.current_player, g.current_mask)
    g.try_cell("r0c1")
    print(g.current_mask)
