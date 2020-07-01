import logging

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class SomeTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(20), nullable=False)

    def __init__(self, val):
        self.value = val


def reset_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    logging.getLogger(__name__).warning("Reset DataBase!")
