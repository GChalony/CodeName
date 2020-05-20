from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField


class ContactForm(FlaskForm):
    email = StringField("Nom ou email")
    msg = TextAreaField("Message")
    submit = SubmitField("envoyer")

