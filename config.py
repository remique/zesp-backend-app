# TODO: Poustawiac jakos legitnie te configi

class Config(object):
	JSON_SORT_KEYS = False
	CORS_HEADERS = 'Content-Type'
	SECRET_KEY = 'pz-backend-2020'
	JWT_SECRET_KEY = 'secret-key'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True