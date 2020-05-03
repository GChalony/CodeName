class User():
    def __init__(self, user_id, pseudo=""):
        self.id = user_id
        self.pseudo = pseudo

    def __repr__(self):
        return f"<nickname={self.pseudo}>"
