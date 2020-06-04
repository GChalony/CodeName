import logging

from flask import render_template, request

from codenameapp.avatar.avatar_manager import AvatarManager
from codenameapp.contact_us.contacts_handler import send_contact_form_as_email, send_words_in_email
from codenameapp.contact_us.forms import ContactForm, ProposeWordsForm

logger = logging.getLogger(__name__)


class RouteManager:
    def init_routes(self, app):
        app.add_url_rule('/', view_func=self.get_home)
        app.add_url_rule('/contact/contact_us', view_func=self.get_contact_us)
        app.add_url_rule('/contact/post_contact', view_func=send_contact_form_as_email,
                         methods=["POST"])
        app.add_url_rule('/contact/propose_words', view_func=self.get_propose_words)
        app.add_url_rule('/contact/post_words', view_func=send_words_in_email, methods=["POST"])

    def get_home(self):
        avatar_path = AvatarManager.choose_random_avatar_img()
        return render_template("home.html",
                               target_room_id=request.args.get("target_room_id"),
                               avatar_src=avatar_path.as_posix(),
                               avatar_id=avatar_path.relative_to('static').as_posix())

    def get_contact_us(self):
        return render_template("contact_us.html", form=ContactForm())

    def get_propose_words(self):
        return render_template("propose_words.html", form=ProposeWordsForm())
