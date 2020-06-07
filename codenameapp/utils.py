import datetime
import json
import logging
import multiprocessing as mp
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterable

import numpy as np
from flask import current_app, request, session


def generate_random_words(path_to_words="static/ressources/words.csv"):
    with open(path_to_words, encoding="utf8") as words_file:
        words = words_file.readlines()
    words = [w.replace("\n", "").capitalize() for w in words]
    np.random.shuffle(words)
    words = words[:25]
    words = [w.capitalize() for w in words]
    return np.array(words).reshape((5, 5))


def parse_array_to_json(a):
    n, m = a.shape
    res = {}
    for r in range(n):
        for c in range(m):
            res[f"r{r}c{c}"] = a[r][c]
    return json.dumps(res)


def parse_cell_code(cell_code):
    r, c = int(cell_code[1]), int(cell_code[3])
    return r, c


def generate_response_grid():
    """1: red, 2: blue, 3: black, 0: nothing"""
    base_array = [1] * 9 + [2] * 8 + [3] + [0] * 7
    np.random.shuffle(base_array)
    map = np.resize(base_array, (5, 5))
    map = np.array(map, dtype=np.uint8)
    return map


def send_email(subject, text_body, html_body):
    from_addr, to_addr = current_app.config["DEFAULT_MAIL_SENDER"], \
                         current_app.config["DEFAULT_MAIL_MONITOR"]

    msg = MIMEMultipart('alternative')
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    txt = MIMEText(text_body, 'plain')
    html = MIMEText(html_body, 'html')
    msg.attach(txt)
    msg.attach(html)

    ctx = mp.get_context("spawn")
    p = ctx.Process(target=send_async_email, args=(current_app.config, msg))
    p.start()


def send_async_email(config, msg):
    import smtplib
    import ssl
    logging.getLogger(__name__).info(f"Sending async email")
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config["MAIL_SERVER"], config["MAIL_PORT"], context=context) as server:
        server.login(config["DEFAULT_MAIL_SENDER"], config["MAIL_PASSWORD"])
        server.sendmail(config["DEFAULT_MAIL_SENDER"], [config["DEFAULT_MAIL_MONITOR"]],
                        msg.as_string())
    logging.getLogger(__name__).debug("Done sending mail")


def read_and_store_avatar_params(resp, user_id):
    """Read pseudo and avator colors from either cookies or request params.
    Then store them in both cookies and session.
    """
    pseudo = request.args.get("pseudo")
    avatar_src = request.args.get("avatar_src")
    if pseudo is None:  # Read from cookies
        pseudo = request.cookies.get("pseudo")
        avatar_src = request.cookies.get("avatar_src")
    if pseudo is None or avatar_src is None:
        raise ValueError("Missing parameter")

    # Add cookies and store data in session
    data_to_store = dict(user_id=user_id, pseudo=pseudo, avatar_src=avatar_src)
    expire_date = datetime.datetime.now() + datetime.timedelta(30)  # 30 days ahead
    for key, val in data_to_store.items():
        session[key] = val
        resp.set_cookie(key, val, expires=expire_date)

    return pseudo, avatar_src

emoji_to_unicode = {
    ":)": "\U0001F60A",
    ":D": "\U0001F601",
    ":p": "\U0001F60B",
    "--": "\U0001F613",
    ";p": "\U0001F61C",
    "XP": "\U0001F61D",
    "xp": "\U0001F61D",
    "Xp": "\U0001F61D",
    "><": "\U0001F623",
    ";,(": "\U0001F622",
    ":'(": "\U0001F622",
    "OMG": "\U0001F631",
    "omg": "\U0001F631"
}

swear_words = [
    "bite", "connard", "con", "couille", "encule", "niquer", "pute", "salaud", "fdp", "salaud"
]


def replace_words(s: str, words_to_replace: Iterable[str], replace_with: str):
    words = s.split()
    res = []
    for word in words:
        if word in words_to_replace:
            res.append(replace_with)
        else:
            res.append(word)
    return " ".join(res)


def parse_for_emojis(msg):
    for key, ucode in emoji_to_unicode.items():
        msg = msg.replace(key, ucode)
    msg = replace_words(msg, swear_words, "\U0001F4A5")  # Censoring
    return msg
