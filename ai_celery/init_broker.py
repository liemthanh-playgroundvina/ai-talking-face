from kombu import Connection
from kombu.exceptions import OperationalError
from configs.env import settings


def is_broker_running(retries: int = 3) -> bool:
    try:
        conn = Connection(settings.BROKER)
        conn.ensure_connection(max_retries=retries)
    except OperationalError as e:
        print("Failed to connect to RabbitMQ instance at %s", settings.BROKER)
        print(str(e))
        return False
    conn.close()
    return True
