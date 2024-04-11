import os
from dotenv import load_dotenv
from pydantic import BaseSettings


print(os.getcwd())

load_dotenv("./configs/.env")


class Settings(BaseSettings):
    AI_QUERY_NAME = os.getenv("AI_QUERY_NAME", "ai_celery")
    AI_TALKING_FACE = os.getenv("AI_TALKING_FACE", "ai_talking_face")
    # REDIS
    REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
    REDIS_PORT = os.getenv("REDIS_PORT", 6379)
    REDIS_PASS = os.getenv("REDIS_PASS", "")
    REDIS_DB = os.getenv("REDIS_DB", 0)
    REDIS_BACKEND = "redis://:{password}@{hostname}:{port}/{db}".format(
        hostname=REDIS_HOST, password=REDIS_PASS, port=REDIS_PORT, db=REDIS_DB
    )
    # RABBITMQ
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "127.0.0.1")
    RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "")
    BROKER = "amqp://{user}:{pw}@{hostname}:{port}/{vhost}".format(
        user=RABBITMQ_USER,
        pw=RABBITMQ_PASS,
        hostname=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        vhost=RABBITMQ_VHOST,
    )

    # S3 KEY
    AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv(
        "AWS_SECRET_ACCESS_KEY", ""
    )
    AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "")
    AWS_ACL = os.getenv("AWS_ACL", "public-read")


settings = Settings()
