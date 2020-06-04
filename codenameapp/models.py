class User:
    def __init__(self, user_id, pseudo="", avatar_src=None):
        self.id = user_id
        self.pseudo = pseudo
        self.avatar_src = avatar_src

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

    def __iter__(self):
        return iter([self.spy, *self.guessers])

    def to_json(self):
        return {"spy": self.spy.to_json() if self.spy is not None else "None",
                "guessers": [g.to_json() for g in self.guessers]}

    def get_ids_list(self):
        return [p.id for p in self]

