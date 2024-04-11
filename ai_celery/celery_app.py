from celery import Celery
from kombu import Queue
from configs.env import settings

app = Celery(settings.AI_QUERY_NAME, broker=settings.BROKER, backend=settings.REDIS_BACKEND)
app.config_from_object({
    'task_acks_late': True,
    'worker_prefetch_multiplier': 1,
    'task_queues': [
        Queue(name=settings.AI_TALKING_FACE),
    ],
    'result_expires': 60 * 60 * 48,
    'task_always_eager': False,
})
