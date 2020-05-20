from flask import render_template, url_for

from codenameapp.contact_us.forms import ContactForm


def send_contact_form_as_email():
    form = ContactForm()
    # Send email here
    print(form.msg)
    return render_template("index.html")


def send_words_in_email():
    pass