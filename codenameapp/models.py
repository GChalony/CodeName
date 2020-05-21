class User():
    def __init__(self, user_id, pseudo="", backcol="#ffff00", mouthcol="#ff0000"):
        self.id = user_id
        self.pseudo = pseudo
        self.backcol = backcol
        self.mouthcol = mouthcol

    def __repr__(self):
        return f"<pseudo={self.pseudo}>"


class Team:
    def __init__(self, spy=None, guessers=None):
        self.spy = spy
        self.guessers = guessers if guessers is not None else []

    def __repr__(self):
        return "<spy={spy} - guessers={guessers}>".format(spy=self.spy, guessers=self.guessers)

    def to_dict(self):
        return {"spy": self.spy, "guessers": self.guessers}
