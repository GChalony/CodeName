import logging

from flask import render_template

from codenameapp.contact_us.forms import ContactForm

logger = logging.getLogger(__name__)


class RouteManager:
    def init_routes(self, app):
        app.add_url_rule('/', view_func=self.get_home)
        app.add_url_rule('/contact_us', view_func=self.get_contact_us)

    def get_home(self):
        return render_template("index.html")

    def get_contact_us(self):
        return render_template("contact_us.html", form=ContactForm())
