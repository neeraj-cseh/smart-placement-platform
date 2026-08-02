from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def sync_contests_job():
    try:
        call_command('sync_contests')
    except Exception as e:
        logger.error(f"Error during scheduled contest sync: {e}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Run the sync_contests_job every 12 hours
    scheduler.add_job(
        sync_contests_job,
        trigger=IntervalTrigger(hours=12),
        id='sync_contests_job',
        name='Sync external contests every 12 hours',
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info("APScheduler started: Background contest synchronization is active.")
