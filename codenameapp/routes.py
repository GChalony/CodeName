import logging

from flask import render_template

from codenameapp.contact_us.contacts_handler import send_contact_form_as_email, send_words_in_email
from codenameapp.contact_us.forms import ContactForm

logger = logging.getLogger(__name__)


class RouteManager:
    def init_routes(self, app):
        app.add_url_rule('/', view_func=self.get_home)
        app.add_url_rule('/contact/contact_us', view_func=self.get_contact_us)
        app.add_url_rule('/contact/post_contact', view_func=send_contact_form_as_email, methods=["POST"])
        app.add_url_rule('/contact/proposer_words', view_func=self.get_propose_words)
        app.add_url_rule('/contact/post_words', view_func=send_words_in_email, methods=["POST"])

    def get_home(self):
        return render_template("index.html")

    def get_contact_us(self):
        return render_template("contact_us.html", form=ContactForm())

    def get_propose_words(self):
        return render_template("propose_words.html")