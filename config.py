import os


SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key")
SESSION_TYPE = os.environ.get("SESSION_TYPE", "filesystem")