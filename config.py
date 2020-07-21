import os

basedir = os.path.abspath(os.path.dirname(__file__))


class AppConfig:
    FLASK_ENVIRON = os.environ.get("FLASK_ENV")
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
    SESSION_TYPE = "sqlalchemy"
    SESSION_COOKIE_SECURE = False  # TODO could be true on Heroku with HTTPS
    SESSION_USE_SIGNER = True
    # DB
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///" +
                                             os.path.join(basedir, "app.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False


default_config = AppConfig()
