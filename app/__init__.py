# Flask app initialization
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///outcast_ranking.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
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