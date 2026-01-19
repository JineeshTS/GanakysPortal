"""
GanaPortal Celery Application Configuration
Background task processing for async operations
"""
import os
from celery import Celery
from kombu import Exchange, Queue

# Get Redis URL from environment or use default
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/3")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/4")

# Create Celery app
celery_app = Celery(
    "ganaportal",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.report_tasks",
        "app.tasks.notification_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,

    # Result settings
    result_expires=86400,  # 24 hours
    result_extended=True,

    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3000,  # 50 minutes soft limit

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Queue configuration
    task_default_queue="default",
    task_queues=(
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
        Queue("low_priority", Exchange("low_priority"), routing_key="low_priority"),
        Queue("emails", Exchange("emails"), routing_key="emails"),
        Queue("reports", Exchange("reports"), routing_key="reports"),
    ),

    # Task routing
    task_routes={
        "app.tasks.email_tasks.*": {"queue": "emails"},
        "app.tasks.report_tasks.*": {"queue": "reports"},
        "app.tasks.notification_tasks.*": {"queue": "high_priority"},
    },

    # Beat schedule for periodic tasks
    beat_schedule={
        "cleanup-expired-sessions": {
            "task": "app.tasks.maintenance_tasks.cleanup_expired_sessions",
            "schedule": 3600.0,  # Every hour
        },
        "daily-report-generation": {
            "task": "app.tasks.report_tasks.generate_daily_reports",
            "schedule": 86400.0,  # Every 24 hours
            "options": {"queue": "reports"},
        },
    },
)

# Optional: Configure for development/production
if os.getenv("APP_ENV") == "development":
    celery_app.conf.update(
        task_always_eager=False,
        task_eager_propagates=True,
    )
