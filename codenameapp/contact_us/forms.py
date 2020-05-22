from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField


class ContactForm(FlaskForm):
    contact = StringField("Nom ou email")
    msg = TextAreaField("Message")
    submit = SubmitField("envoyer")


class ProposeWordsForm(FlaskForm):
    contact = StringField("Nom ou email")
    words = TextAreaField("Vos mots")
    submit = SubmitField("envoyer")
