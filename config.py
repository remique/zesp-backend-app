# TODO: Poustawiac jakos legitnie te configi

class Config(object):
    JSON_SORT_KEYS = False
    CORS_HEADERS = 'Content-Type'
    SECRET_KEY = 'pz-backend-2020'
    JWT_SECRET_KEY = 'secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SCHEDULER_API_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    JWT_SECRET_KEY = 'secret-key'
