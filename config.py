# Configuration settings
import os
import secrets

class Config:
    # Security: Use environment variable or generate a random key
    # IMPORTANT: Set SECRET_KEY environment variable in production!
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Database
    # PostgreSQL support: Render uses 'postgresql://' but SQLAlchemy 1.4+ requires 'postgresql://'
    # Older postgres:// URLs need to be converted to postgresql://
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///outcast_ranking.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Headers
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour