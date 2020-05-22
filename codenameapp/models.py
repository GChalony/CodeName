class User:
    def __init__(self, user_id, pseudo="", backcol="#ffff00", mouthcol="#ff0000"):
        self.id = user_id
        self.pseudo = pseudo
        self.backcol = backcol
        self.mouthcol = mouthcol

    def __repr__(self):
        return f"<pseudo={self.pseudo}, id={self.id}>"

    def to_json(self):
        return self.__dict__


class Team:
    def __init__(self, spy=None, guessers=None):
        self.spy = spy
        self.guessers = guessers if guessers is not None else []

    def __repr__(self):
        return "<spy={spy} - guessers={guessers}>".format(spy=self.spy, guessers=self.guessers)

    def to_json(self):
        return {"spy": self.spy.to_json() if self.spy is not None else "None",
                "guessers": [g.to_json() for g in self.guessers]}

    def get_ids_list(self):
        guessers_ids = [g.id for g in self.guessers]
        return [self.spy.id, *guessers_ids]

