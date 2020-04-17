"""S3 Client"""
#pylint: disable=too-few-public-methods
import boto3
from service.resources.file_client import FileClientInterface

class S3Client(FileClientInterface):
    """S3 Client class"""
    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_bucket_name):
        self.client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.bucket_name = aws_bucket_name

    def download_file(self, object_name, file_path):
        #pylint: disable=no-self-use
        """
            retrieve file object s3 and return it
        """
        self.client.download_file(self.bucket_name, object_name, file_path)
