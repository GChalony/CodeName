import logging
from datetime import datetime

from flask import render_template, url_for

from codenameapp.contact_us.forms import ContactForm, ProposeWordsForm
from codenameapp.utils import send_email

# TODO check forms not empty
logger = logging.getLogger(__name__)


def send_contact_form_as_email():
    form = ContactForm()
    # Send email here
    time = datetime.now()
    logger.info(f"Sending message in email.")
    send_email("Message de Enigma",
               f"Message de {form.contact.data} envoyé à {time}\n\n"
               f"Message:\n{form.msg.data}",
               f"<h3>Message de {form.contact.data} envoyé à {time}</h3>\n"
               f"<p>{form.msg.data}</p>"
               )
    return render_template("index.html")


def send_words_in_email():
    form = ProposeWordsForm()
    time = datetime.now()
    logger.info("Sending email for words.")
    send_email("Proposition de mots",
               f"Message de {form.contact.data} envoyé à {time}\n\n"
               f"Message:\n{form.words.data}",
               f"<h3>Message de {form.contact.data} envoyé à {time}</h3>\n"
               f"<p>{form.words.data}</p>"
               )
    return render_template("index.html")
