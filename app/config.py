#config.py

import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///data/ntsoekhe.db"
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OTHER_NODES = [
        'https://172.0.0.1:8081',
        'https://172.0.0.2:8082',
        'https://172.0.0.3:8083',
        'https://172.0.0.4:8084',
        'https://172.0.0.5:8085'
    ]

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    pass  # Add production-specific configurations here (e.g., logging, security)

def get_app_config(environment):
    if environment == 'development':
        return DevelopmentConfig
    elif environment == 'testing':
        return TestingConfig
    elif environment == 'production':
        return ProductionConfig
    else:
        raise InvalidEnvironmentError(f'Invalid environment: {environment}')

class InvalidEnvironmentError(Exception):
    pass

# Choose the appropriate configuration based on the environment
environment = os.environ.get('FLASK_ENV', 'development')  # Default to development
app_config = get_app_config(environment)
