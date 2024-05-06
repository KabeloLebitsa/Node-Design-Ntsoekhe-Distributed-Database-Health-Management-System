#config.py

import os
import logging

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///data/ntsoekhe.db"
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_TRACK_MODIFICATIONS = False       
    REQUEST_CACHE_EXPIRY_SECONDS = 300 
    DATA_DIR = "data" 
    NODES = [
        'http://172.0.0.1:8081',
        'http://172.0.0.2:8082',
        'http://172.0.0.3:8083',
        'http://172.0.0.4:8084',
        'http://172.0.0.5:8085'
    ]

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s %(levelname)s %(message)s'
            },
        },
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': 'app.log',
                'mode': 'a',
                'formatter': 'standard',
            },
        },
        'loggers': {
            'app': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': False,
            },
        }
    }

    # Add production-specific configurations here (e.g., security settings)

def get_app_config(environment):
    if environment == 'development':
        return DevelopmentConfig()
    elif environment == 'testing':
        return TestingConfig()
    elif environment == 'production':
        return ProductionConfig()
    else:
        raise InvalidEnvironmentError(f'Invalid environment: {environment}')

class InvalidEnvironmentError(Exception):
    pass

# Choose the appropriate configuration based on the environment
environment = os.environ.get('FLASK_ENV', 'development')  # Default to development
app_config = get_app_config(environment)
