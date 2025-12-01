from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Manager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ManagerStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('manager.id'), nullable=False)
    season = db.Column(db.String(4), nullable=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    win_percentage = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    manager = db.relationship('Manager', backref=db.backref('stats', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('manager_id', 'season'),)

class LeagueCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(50), nullable=False)  # Which user this record is for
    season = db.Column(db.String(4), nullable=False)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    team_name = db.Column(db.String(100), nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('league_id', 'user_id', 'season'),)

class UserSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usernames = db.Column(db.Text, nullable=False)  # Comma-separated usernames
    season = db.Column(db.String(4), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_processed = db.Column(db.DateTime, nullable=True)