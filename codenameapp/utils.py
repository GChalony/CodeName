import datetime
import json
import logging
import multiprocessing as mp
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import numpy as np
from flask import current_app, request, session


def generate_random_words(path_to_words="ressources/words.csv"):
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
    col1 = request.args.get("col1")
    col2 = request.args.get("col2")
    if pseudo is None:  # Read from cookies
        pseudo = request.cookies.get("pseudo")
        col1 = request.cookies.get("avatar_col1")
        col2 = request.cookies.get("avatar_col2")
    if pseudo is None or col1 is None or col2 is None:
        raise ValueError("Missing parameter")

    # Add cookies and store data in session
    data_to_store = dict(user_id=user_id, pseudo=pseudo, avatar_col1=col1, avatar_col2=col2)
    expire_date = datetime.datetime.now() + datetime.timedelta(30)  # 30 days ahead
    for key, val in data_to_store.items():
        session[key] = val
        resp.set_cookie(key, val, expires=expire_date)

    return pseudo, col1, col2