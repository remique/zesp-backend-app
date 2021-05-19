# TODO: Poustawiac jakos legitnie te configi
import os
import re


class Config(object):
    JSON_SORT_KEYS = False
    CORS_HEADERS = 'Content-Type'
    SECRET_KEY = 'pz-backend-2020'
    JWT_SECRET_KEY = 'secret-key'
    SCHEDULER_API_ENABLED = False
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    uri = os.getenv("DATABASE_URL")

    if uri is not None:
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = uri


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    JWT_SECRET_KEY = 'secret-key'
