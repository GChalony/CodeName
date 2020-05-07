class User():
    def __init__(self, user_id, pseudo="", backcol="#ffff00", mouthcol="#ff0000"):
        self.id = user_id
        self.pseudo = pseudo
        self.backcol = backcol
        self.mouthcol = mouthcol

    def __repr__(self):
        return f"<pseudo={self.pseudo}>"
