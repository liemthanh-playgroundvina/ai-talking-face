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
    'broker_transport_options': {
        'visibility_timeout': 3600,
        'max_retries': 5,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.5,
    },
    'worker_cancel_long_running_tasks_on_connection_loss': True,
})
