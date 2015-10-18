import inspect
import importlib
import logging

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError


def setup_logging():
    logging.basicConfig(level=logging.INFO)


def find_classes(module, cls):
    def predicate(obj):
        return inspect.isclass(obj) and issubclass(obj, cls) and obj is not cls
    members = inspect.getmembers(module, predicate)
    return [obj for name, obj in members]


class ClassLoaderFromModule(object):
    def __init__(self, cls):
        self.cls = cls

    def __call__(self, arg):
        module = importlib.import_module(arg)
        classes = find_classes(module, self.cls)
        return classes


def get_swf_connection():
    # Must increase the http timeout since SWF has a timeout of 60 sec
    config = Config(connect_timeout=50, read_timeout=70)
    connection = boto3.client("swf", region_name='us-east-1', config=config)
    return connection


def register_workflow(connection, domain, workflow):
    args = {'default%s' % k: v for k, v in workflow.defaults.items()}
    if 'defaultTaskList' in args:
        args['defaultTaskList'] = {'name': args['defaultTaskList']}
    description = getattr(workflow, 'description', None)
    if description:
        args['description'] = description

    try:
        connection.register_workflow_type(
            domain=domain,
            name=workflow.name,
            version=workflow.version,
            **args
            )

    except ClientError as err:
        error_code = err.response['Error']['Code']
        if error_code == 'TypeAlreadyExistsFault':
            return False  # Ignore this error
        raise

    return True


def is_response_success(response):
    status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
    return status_code == 200
