"""File module"""
#pylint: disable=too-few-public-methods
import os
import json
import falcon
import jsend
import botocore
import magic
from service.resources.amazon.s3.s3_client import S3Client
from service.resources.hooks import validate_access

@falcon.before(validate_access)
class File(S3Client):
    """File class"""
    TEMP_FILE_DIR = "tmp/"

    def on_get(self, _req, resp):
        #pylint: disable=no-self-use
        """on get request
            retrieve file object s3 and return it
        """
        try:
            if set(['name']).issubset(_req.params.keys()):
                object_name = _req.params['name']
                temp_file_path = os.path.join(self.TEMP_FILE_DIR, object_name.replace('/', '-'))

                # download from s3
                print("bucketname:" + self.bucket_name)
                self.client.download_file(self.bucket_name, object_name, temp_file_path)
                # determine content type
                mime = magic.Magic(mime=True)
                resp.content_type = mime.from_file(temp_file_path)

                # build response
                resp.status = falcon.HTTP_200
                with open(temp_file_path, 'rb') as f: # pylint: disable=invalid-name
                    resp.body = f.read()

                # cleanup
                os.remove(temp_file_path)
            else:
                raise Exception('The name parameter is required')

        except botocore.exceptions.ClientError as err:
            if err.response['Error']['Code'] == "404":
                resp.status = falcon.HTTP_404
                resp.body = json.dumps(jsend.error("The object does not exist"))
            else:
                resp.status = falcon.HTTP_500
                resp.body = json.dumps(jsend.error(err.response['Error']['Message']))
        except Exception as err: # pylint: disable=broad-except
            resp.status = falcon.HTTP_500
            resp.body = json.dumps(jsend.error("{0}".format(err)))
