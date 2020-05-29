import os


class AppConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "309D16F75DE58E676159E641BE92AA5C6CBF131EC73B89CE")
    # Mail config
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    DEFAULT_MAIL_SENDER = "enigma.heroku@gmail.com"
    MAIL_USERNAME = "enigma.heroku@gmail.com"
    MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
    DEFAULT_MAIL_MONITOR = "enigma.heroku.monitor@gmail.com"
    # Session config
    SESSION_TYPE = "filesystem"
    SESSION_COOKIE_SECURE = True
    SESSION_USE_SIGNER = True




default_config = AppConfig()
