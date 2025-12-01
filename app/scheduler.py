from apscheduler.schedulers.background import BackgroundScheduler
from .services.ranking import refresh_all_data
import atexit

scheduler = None

def init_scheduler(app):
    global scheduler
    scheduler = BackgroundScheduler()
    
    # Schedule weekly refresh on Tuesdays at 9 AM (after Monday night games)
    scheduler.add_job(
        func=refresh_weekly_data,
        trigger="cron",
        day_of_week=1,  # Tuesday
        hour=9,
        minute=0,
        args=[app]
    )
    
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

def refresh_weekly_data(app):
    with app.app_context():
        try:
            refresh_all_data()
        except Exception as e:
            app.logger.error(f"Error refreshing weekly data: {e}")