"""Main application module"""
import os
import json
import jsend
import sentry_sdk
import falcon
from .resources.amazon.s3.file import File
from .resources.welcome import Welcome

def start_service():
    """Start this service
    set SENTRY_DSN environmental variable to enable logging with Sentry
    """
    # Initialize Sentry
    sentry_sdk.init(os.environ.get('SENTRY_DSN'))
    # Initialize Falcon
    api = falcon.API()
    api.add_route('/bucketeer/file', File(os.environ.get('BUCKETEER_AWS_ACCESS_KEY_ID'),\
            os.environ.get('BUCKETEER_AWS_SECRET_ACCESS_KEY'),\
            os.environ.get('BUCKETEER_AWS_BUCKET_NAME')))
    api.add_route('/welcome', Welcome())
    api.add_sink(default_error, '')
    return api

def default_error(_req, resp):
    """Handle default error"""
    resp.status = falcon.HTTP_404
    msg_error = jsend.error('404 - Not Found')

    sentry_sdk.capture_message(msg_error)
    resp.body = json.dumps(msg_error)
