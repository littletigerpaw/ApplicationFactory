import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "backendp1-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "backendp1-jwt-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///backendp1.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 60
    RATELIMIT_DEFAULT = "200 per day; 50 per hour"
    RATELIMIT_STORAGE_URI = "memory://"
