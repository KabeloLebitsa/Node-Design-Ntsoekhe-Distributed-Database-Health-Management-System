import os

class Config:
    #SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')  # Use environment variable for secret key
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///ntsoekhe.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OTHER_NODES = [
        'https://172.18.0.4:8083',
        'https://172.18.0.3:8082',
        'https://172.18.0.2:8081',
        'https://172.18.0.5:8084',
        'https://172.18.0.6:8085'
    ]

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

class ProductionConfig(Config):
    pass  # Add production-specific configurations here (e.g., logging, security)

# Choose the appropriate configuration based on the environment
environment = os.environ.get('FLASK_ENV', 'development')  # Default to development

if environment == 'development':
    app_config = DevelopmentConfig
elif environment == 'testing':
    app_config = TestingConfig
elif environment == 'production':
    app_config = ProductionConfig
else:
    raise Exception(f'Invalid environment: {environment}')
