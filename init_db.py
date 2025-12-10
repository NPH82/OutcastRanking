"""
Database initialization script
Run this after deploying to create tables in PostgreSQL
"""
from app import create_app, db

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Database tables created successfully!")
    
    # Print table names
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"📊 Created tables: {', '.join(tables)}")
