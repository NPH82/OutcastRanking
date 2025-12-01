# Configuration settings
import os
import secrets

class Config:
    # Security: Use environment variable or generate a random key
    # IMPORTANT: Set SECRET_KEY environment variable in production!
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///outcast_ranking.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Headers
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour