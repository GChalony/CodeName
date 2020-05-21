import os


class AppConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key")
    SESSION_TYPE = os.environ.get("SESSION_TYPE", "filesystem")
    # Mail config
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    DEFAULT_MAIL_SENDER = "enigma.heroku@gmail.com"
    MAIL_USERNAME = "enigma.heroku@gmail.com"
    MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
    MAIL_DEFAULT_MONITOR = "enigma.heroku.monitor@gmail.com"


default_config = AppConfig()
