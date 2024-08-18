import multiprocessing
import os
from celery import Celery

multiprocessing.set_start_method('fork', force=True)

celery_app = Celery(
    "detection_tasks",
    broker="redis://localhost:6379/0",
    backend=os.environ.get('CELERY_BACKEND')
)

import app.tasks
