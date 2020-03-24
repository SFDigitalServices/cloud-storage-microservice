"""S3 Client"""
#pylint: disable=too-few-public-methods
import boto3

class S3Client():
    """S3 Client class"""
    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_bucket_name):
        self.client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.bucket_name = aws_bucket_name
