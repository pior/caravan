import boto3
from botocore.client import Config


def get_swf_connection():
    # Must increase the http timeout since SWF has a timeout of 60 sec
    config = Config(connect_timeout=50, read_timeout=70)
    connection = boto3.client("swf", region_name='us-east-1', config=config)
    return connection


def is_response_success(response):
    status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
    return status_code == 200
