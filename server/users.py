class User():
    def __init__(self, user_id):
        self.id = user_id
        self.nickname = ""

    def __repr__(self):
        return f"<{self.id}>"
