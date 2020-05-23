import json
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process

import numpy as np
from flask import current_app


def generate_random_words(path_to_words="ressources/words.csv"):
    with open(path_to_words, encoding="utf8") as words_file:
        words = words_file.readlines()
    words = [w.replace("\n", "").capitalize() for w in words]
    np.random.shuffle(words)
    words = words[:25]
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
    p = Process(target=send_async_email, args=(current_app.config, msg))
    p.start()


def send_async_email(config, msg):
    # Revert monkey patch
    import sys
    del sys.modules["socket"]
    sys.modules["socket"] = __import__("socket")

    import ssl
    import smtplib
    logging.getLogger(__name__).info(f"Sending async email")
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config["MAIL_SERVER"], config["MAIL_PORT"], context=context) as server:
        server.login(config["DEFAULT_MAIL_SENDER"], config["MAIL_PASSWORD"])
        server.sendmail(config["DEFAULT_MAIL_SENDER"], [config["DEFAULT_MAIL_MONITOR"]],
                        msg.as_string())
    logging.getLogger(__name__).debug("Done sending mail")

