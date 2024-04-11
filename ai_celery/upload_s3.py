import mimetypes
from typing import Optional, Text, Tuple
from datetime import datetime

import os

import requests

from configs.env import settings


def upload_file(file, folder):
    """
    This function uploads a file to an AWS S3 bucket and returns the file's key and URL.

    :param file: The file parameter is the file object that needs to be uploaded to the S3 bucket
    :param folder: The folder parameter is a string that represents the name of the folder in which the
    file will be uploaded to in the AWS S3 bucket
    :return: a dictionary with two keys: "key" and "url".
    """
    try:
        s3_client = getS3()
        file_name = file.filename
        s3_key = os.path.join(folder, file_name)
        # save file to s3
        s3_client.upload_fileobj(
            file.file,
            settings.AWS_BUCKET_NAME,
            s3_key,
            ExtraArgs={'ContentType': f'{file.mimetype}; charset=utf-8'}
        )
        # set role read file
        s3_client.put_object_acl(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=s3_key,
            ACL='public-read'
        )
        object_url = f"https://{settings.AWS_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
        return {
            "message": "Upload file success.",
            "success": True,
            "data": {
                "key": file_name,
                "url": object_url
            }
        }
    except Exception as e:
        print("============================== ERROR UPLOAD FILE =================================")
        print(str(e))
        return {
            "message": str(e),
            "success": False,
            "data :": {
                "key": '',
                "url": ''
            }
        }


def delete_file(key, folder):
    """
    This function deletes a file from an S3 bucket using the provided key and folder.

    :param key: The name of the file to be deleted from the S3 bucket
    :param folder: The folder parameter is the name of the folder in which the file to be deleted is
    located
    :return: a boolean value indicating whether the file was successfully deleted or not. True is
    returned if the file was deleted successfully, and False is returned if there was an error while
    deleting the file.
    """
    try:
        s3_client = getS3()
        s3_key = os.path.join(folder, key)
        # delete file by key
        s3_client.delete_object(Bucket=settings.AWS_BUCKET_NAME, Key=s3_key)
        return True
    except Exception as e:
        print("============================== ERROR DELTE FILE =================================")
        print(str(e))
        return False


def getS3():
    """
    This function returns an S3 client object configured with AWS access keys and region settings from
    the provided settings file.
    :return: The function `getS3()` is returning an instance of the `boto3.client` class for Amazon S3,
    which is configured with the AWS access key ID, secret access key, and region specified in the
    `settings` module.
    """
    import boto3

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    return s3_client


def load_file_from_s3(file_url: str) -> Tuple[Text, Text]:
    """
    This function downloads a file from an AWS S3 bucket using the provided file URL
    and returns a NamedTemporaryFile with the downloaded content.

    :param file_url: The URL of the file to be downloaded from the S3 bucket.
    :return: A NamedTemporaryFile object containing the downloaded file if successful, or None if an error occurs.
    """
    try:
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            temp_dir = os.path.join(settings.STATIC_URL, "s3_download")
            os.makedirs(temp_dir, exist_ok=True)
            ts = datetime.now()
            filename = ts.strftime("%Y_%m_%d_%H_%M_%S_%f")[:-3]
            file_path = os.path.join(temp_dir, f"{filename}_{os.path.basename(file_url)}")
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=128):
                    f.write(chunk)

            headers = response.headers
            content_type, _ = mimetypes.guess_type(file_path)
            headers['Content-Type'] = content_type

            return file_path, headers
        else:
            raise Exception(f"Can't read file from url: {file_url}")
    except Exception as e:
        raise e


def check_path(file_path):
    client = getS3()
    result = client.list_objects(Bucket=settings.AWS_BUCKET_NAME, Prefix=file_path)
    exists = False
    if 'Contents' in result:
        exists = True
    return exists