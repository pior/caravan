import importlib
import inspect
import sys

import boto3
from botocore.exceptions import ClientError
from botocore.client import Config


def get_swf_connection():
    # Must increase the http timeout since SWF has a timeout of 60 sec
    config = Config(connect_timeout=50, read_timeout=70)
    connection = boto3.client("swf", region_name='us-east-1', config=config)
    return connection


def is_response_success(response):
    status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
    return status_code == 200


def run_swf_command(command, **kwargs):
    connection = get_swf_connection()
    command = getattr(connection, command)

    callargs = {k: v for k, v in kwargs.items() if v is not None}

    try:
        response = command(**callargs)
    except ClientError as err:
        sys.exit(err)
    else:
        if is_response_success(response):
            response.pop('ResponseMetadata')
            return response
        else:
            sys.exit('Error: %s' % response)


def find_classes(module, cls):
    def predicate(obj):
        return inspect.isclass(obj) and issubclass(obj, cls) and obj is not cls
    members = inspect.getmembers(module, predicate)
    return [obj for name, obj in members]


class ClassesLoaderFromModule(object):

    """Load and return classes in a module that inherit from a class.

    This module must be in the python sys path.
    """

    def __init__(self, cls):
        self.cls = cls

    def __repr__(self):
        return '<ClassesLoader(%s)>' % self.cls.__name__

    def __call__(self, arg):
        sys.path.append('.')
        try:
            module = importlib.import_module(arg)
        finally:
            sys.path.pop()

        classes = find_classes(module, self.cls)
        if not classes:
            raise ValueError("No workflow in module %s" % arg)

        return classes
