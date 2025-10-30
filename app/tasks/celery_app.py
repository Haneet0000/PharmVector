from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "pharmvector",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.tasks.embeddings']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
