import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mgnrega-gujarat-secret-2024'
    DATABASE_PATH = 'database/mgnrega.db'
    CACHE_TIMEOUT = 3600  # 1 hour
    API_RATE_LIMIT = 100  # requests per hour
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False