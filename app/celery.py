import multiprocessing
import os
from celery import Celery

multiprocessing.set_start_method('fork', force=True)

celery_app = Celery(
    "detection_tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)
celery_app.conf.task_routes = {
    "app.worker.detection_tasks": "main-queue",
}
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

import app.tasks
