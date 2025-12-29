"""Celery application configuration for background tasks"""

from celery import Celery
from config import Config

def make_celery(app_name=__name__):
    """Create and configure Celery app"""
    celery = Celery(
        app_name,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=['app.tasks.match_tasks']
    )
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=1000,
    )
    # Configure periodic tasks
    celery.conf.beat_schedule = {
        'fetch-live-matches-every-30-seconds': {
            'task': 'app.tasks.match_tasks.fetch_live_matches',
            'schedule': 30.0,  # 30 seconds
        },
        'update-odds-every-5-minutes': {
            'task': 'app.tasks.match_tasks.update_match_odds',
            'schedule': 300.0,  # 5 minutes
        },
        'fetch-upcoming-matches-every-hour': {
            'task': 'app.tasks.match_tasks.fetch_upcoming_matches',
            'schedule': 3600.0,  # 1 hour
        },
        'settle-finished-matches-every-2-minutes': {
            'task': 'app.tasks.match_tasks.settle_finished_matches',
            'schedule': 120.0,  # 2 minutes
        },
    }
    return celery

celery = make_celery()
