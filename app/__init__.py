# Flask app initialization
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///outcast_ranking.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Security headers
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if os.environ.get('FLASK_ENV') == 'production':
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    # Initialize extensions
    from .models import db
    db.init_app(app)
    
    # Register blueprints
    from .routes import main
    from .manager_routes import manager_bp
    
    app.register_blueprint(main, url_prefix='/old')  # Keep old functionality
    app.register_blueprint(manager_bp)  # New manager search as main
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Initialize scheduler
    from .scheduler import init_scheduler
    init_scheduler(app)
    
    return app