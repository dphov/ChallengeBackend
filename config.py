from os import environ, path
from dotenv import load_dotenv
import redis

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))


class Config:
    """
    Set Flask configuration vars from .env file.
    """

    # Postgres config
    DATABASE_NAME = environ.get("DATABASE_NAME")
    DATABASE_USER = environ.get("DATABASE_USER")
    DATABASE_PASSWORD = environ.get("DATABASE_PASSWORD")
    DATABASE_HOST = environ.get("DATABASE_HOST")
    DATABASE_PORT = environ.get("DATABASE_PORT")

    # Redis config
    REDIS_PASSWORD = environ.get("REDIS_PASSWORD")
    REDIS_HOST = environ.get("REDIS_HOST")
    REDIS_PORT = environ.get("REDIS_PORT")

    # SqlAlchemy config
    SQLALCHEMY_DATABASE_URI = (
        "postgres://"
        + DATABASE_USER
        + ":"
        + DATABASE_PASSWORD
        + "@"
        + DATABASE_HOST
        + ":"
        + DATABASE_PORT
        + "/"
        + DATABASE_NAME
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    # Flask-Session
    SESSION_TYPE = environ.get("SESSION_TYPE")
    SESSION_REDIS = redis.from_url(
        "redis://:" + REDIS_PASSWORD + "@" + REDIS_HOST + ":" + REDIS_PORT
    )
