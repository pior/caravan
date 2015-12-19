import importlib
import inspect
import sys

import boto3
from botocore.exceptions import ClientError
from caravan.swf import get_connection


def run_swf_command(command_name, **kwargs):
    connection = kwargs.get('connection')
    if connection is None:
        connection = get_connection()

    command = getattr(connection, command_name)

    callargs = {k: v for k, v in kwargs.items() if v is not None}

    try:
        response = command(**callargs)
    except ClientError as err:
        sys.exit(err)
    else:
        metadata = response.pop('ResponseMetadata', {})
        success = metadata.get('HTTPStatusCode') == 200
        if success:
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
