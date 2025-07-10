import boto3
from app.config import AWS_REGION, S3_BUCKET

s3_client = boto3.client('s3', region_name=AWS_REGION)

def upload_fileobj(fileobj, key):
    s3_client.upload_fileobj(fileobj, S3_BUCKET, key)

def list_user_files(prefix):
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=prefix)
    return [obj['Key'].split('/', 1)[-1] for obj in response.get('Contents', [])]

def download_fileobj(key, fileobj):
    s3_client.download_fileobj(S3_BUCKET, key, fileobj)
