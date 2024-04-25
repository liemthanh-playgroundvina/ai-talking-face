import os
import json
from datetime import datetime

from ai_celery.mq_main import redis


class Celery_RedisClient(object):
    __instance = None

    @staticmethod
    def started(task_id: str, data: dict):
        data['status']['general_status'] = "SUCCESS"
        data['status']['task_status'] = "STARTED"
        data_dump = json.dumps(data)
        redis.set(task_id, data_dump)

    @staticmethod
    def failed(task_id: str, data: dict, err: dict):
        data['time']['end_generate'] = str(datetime.utcnow().timestamp())
        data['status']['task_status'] = "FAILED"
        data['error'] = err
        data_dump = json.dumps(data)
        redis.set(task_id, data_dump)

    @staticmethod
    def success(task_id: str, data: dict, response: dict):
        data['time']['end_generate'] = str(datetime.utcnow().timestamp())
        data['status']['task_status'] = "SUCCESS"
        data['task_result'] = response
        data_dump = json.dumps(data)
        redis.set(task_id, data_dump)

    @staticmethod
    def check_task_removed(task_id: str):
        json_tasks_removed = redis.get("tasks_removed")
        if not json_tasks_removed:
            tasks_removed = []
            redis.set("tasks_removed", json.dumps(tasks_removed))
        else:
            tasks_removed = json.loads(json_tasks_removed)

        if task_id in tasks_removed:
            tasks_removed.remove(task_id)
            raise ValueError("Task killed!")


class CommonCeleryService(object):
    __instance = None

    @staticmethod
    def upload_s3_file(file_path: str, content_type: str, folder_in_s3: str):
        from ai_celery.upload_s3 import upload_file

        with open(file_path, "rb") as file:
            file_to_upload = S3UploadFileObject(filename=os.path.basename(file_path), file=file, mimetype=content_type)
            uploaded = upload_file(file_to_upload, folder_in_s3)
            if uploaded['success']:
                return {'url': uploaded['data']['url'],
                        'meta_data': {
                            'filename': os.path.basename(file_path),
                            'storage': 's3'
                        }}
            else:
                raise Exception(f"Failed to upload s3 file:\n {uploaded}")


class S3UploadFileObject(object):
    filename = None
    file = None

    def __init__(self, filename, file, mimetype) -> None:
        self.filename = filename
        self.file = file
        self.mimetype = mimetype
