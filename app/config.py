import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')  # Use environment variable for secret key
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///ntsoekhe.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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
