from redis import Redis
from redis.exceptions import ConnectionError
from configs.env import settings


def is_backend_running() -> bool:
    try:
        conn = Redis(
            host=settings.REDIS_HOST,
            port=int(settings.REDIS_PORT),
            db=int(settings.REDIS_DB),
            password=settings.REDIS_PASS
        )
        conn.client_list()  # Must perform an operation to check connection.
    except ConnectionError as e:
        print("Failed to connect to Redis instance at %s", settings.REDIS_BACKEND)
        print(repr(e))
        return False
    conn.close()
    return True
