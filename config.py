# TODO: Poustawiac jakos legitnie te configi
import os


class Config(object):
    JSON_SORT_KEYS = False
    CORS_HEADERS = 'Content-Type'
    SECRET_KEY = 'pz-backend-2020'
    JWT_SECRET_KEY = 'secret-key'
    SCHEDULER_API_ENABLED = False
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@localhost/test_database'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    JWT_SECRET_KEY = 'secret-key'
