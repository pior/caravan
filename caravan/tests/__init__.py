import os

import boto3


def setUpModule():
    # Setup Fake AWS Keys (this takes precedence over config file)
    os.environ['AWS_ACCESS_KEY_ID'] = 'AK000000000000000000'
    os.environ['AWS_SECRET_ACCESS_KEY'] = (
        '0000000000000000000000000000000000000000')
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

    # Reset previously created default session (for credentials)
    boto3.setup_default_session()
