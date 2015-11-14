import importlib
import inspect
import sys


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
