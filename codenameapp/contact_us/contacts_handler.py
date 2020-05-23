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
    html_words = form.msg.data.replace("\n", "<br/>")
    logger.info(f"Sending message in email.")
    send_email("Message d'un utilisateur",
               f"Message de {form.contact.data}\n"
               f"\tenvoyé à {time}\n\n"
               f"Message:\n{form.msg.data}",
               f"<h3>Message de <i>{form.contact.data}</i></h3>\n"
               f"<p><i>envoyé à {time}</i></p>\n"
               f"<p style='padding: 20px'>{html_words}</p>"
               )
    return render_template("index.html")


def send_words_in_email():
    form = ProposeWordsForm()
    time = datetime.now()
    logger.info("Sending email for words.")
    send_email("Proposition de mots",
               f"Message de {form.contact.data}\n"
               f"\tenvoyé à {time}\n\n"
               f"Message:\n{form.words.data}",
               f"<h3>Message de <i>{form.contact.data}</i></h3>"
               f"<p><i>envoyé à {time}</i></p>\n"
               f"{form.words}"
               )
    return render_template("index.html")
