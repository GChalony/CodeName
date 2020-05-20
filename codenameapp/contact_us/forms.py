from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, SubmitField
from wtforms.fields.html5 import EmailField


class ContactForm(FlaskForm):
    email = EmailField("email")
    contact_me = BooleanField("me contacter")
    msg = TextAreaField("message")
    submit = SubmitField("envoyer")

