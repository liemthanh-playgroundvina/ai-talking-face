import json
import os.path
from datetime import datetime

from celery import Task
from ai_celery.celery_app import app
from configs.env import settings
from ai_celery.common import Celery_RedisClient, CommonCeleryService

from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

from inference import predict_talking_face


class AITalkingFaceTask(Task):
    """
    Abstraction of Celery's Task class to support AI Talking Face
    """
    abstract = True

    def __init__(self):
        super().__init__()

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)


@app.task(
    bind=True,
    base=AITalkingFaceTask,
    name="{query}.{task_name}".format(
        query=settings.AI_QUERY_NAME,
        task_name=settings.AI_TALKING_FACE
    ),
    queue=settings.AI_TALKING_FACE
)
def ai_talking_face_task(self, task_id: str, data: bytes, task_request: bytes, file: bytes):
    """
    Service AI Talking Face tasks

    task_request example:
        file: {
            'audio_voice': {'content_type': 'audio/mpeg', 'filename': 'static/public/ai_cover_gen/voice.mp3'},
            'audio_background': {'content_type': 'audio/mpeg', 'filename': 'static/public/ai_cover_gen/bg.mp3'},
            'image': {'content_type': 'image/png', 'filename': 'static/public/ai_cover_gen/image.png'},
        }
    """
    print("============= AI Talking Face task: Started ===================")
    try:
        # Load data
        data = json.loads(data)
        request = json.loads(task_request)
        file = json.loads(file)
        Celery_RedisClient.started(task_id, data)

        # Request
        voice_path = file.get('audio_voice')['filename'].split('/')[-1]
        voice_path = os.path.join("/app/static/public/ai_cover_gen", voice_path)
        background_path = file.get('audio_background')['filename'].split('/')[-1]
        background_path = os.path.join("/app/static/public/ai_cover_gen", background_path)
        image_path = file.get('video')['filename'].split('/')[-1]
        image_path = os.path.join("/app/static/public/ai_cover_gen", image_path)
        print(image_path, voice_path, background_path)

        # Predict
        talking_face_file = generate(image_path, voice_path, background_path)
        print(talking_face_file)

        # Save s3
        url_file = CommonCeleryService.upload_s3_file(
            talking_face_file,
            "video/mp4",
            "ai_cover_gen"
        )
        # Successful
        metadata = {
            "task": settings.AI_TALKING_FACE,
            "tool": "local",
            "model": "SadTalker",
            "usage": None,
        }
        response = {"url_file": url_file, "metadata": metadata}
        Celery_RedisClient.success(task_id, data, response)
        return
    except ValueError as e:
        err = {'code': "400", 'message': str(e).split('!')[0].strip()}
        Celery_RedisClient.failed(task_id, data, err)
        return
    except Exception as e:
        print(str(e))
        err = {'code': "500", 'message': "Internal Server Error"}
        Celery_RedisClient.failed(task_id, data, err)
        return


def generate(image, audio, background_audio):
    # Face Talking predict
    path_predicted = predict_talking_face(audio, image)

    # Add background audio
    video_clip = VideoFileClip(path_predicted)
    audio_clip = AudioFileClip(background_audio)

    composite_audio = CompositeAudioClip([video_clip.audio, audio_clip])
    video_clip.audio = composite_audio

    now = datetime.now()
    formatted_time = now.strftime(f"%Y_%m_%d_%H_%M_%S_{now.microsecond / 1000:.4f}")
    filename = formatted_time.replace('.', '_')
    path_final = os.path.join("./static/public/ai_cover_gen", f"{filename}.mp4")

    video_clip.write_videofile(
        path_final,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )

    return path_final
