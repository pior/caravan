import argparse
import ConfigParser
import importlib
import inspect
import logging
import sys


class BaseCommand(object):

    """Base class for command-line tools."""

    default_config_section = 'caravan'

    @classmethod
    def main(cls):
        cmd = cls()
        cmd._parse_args()
        cmd._setup_logging()
        cmd._run()

    def _parse_args(self):
        # Config only parser
        config_parser = argparse.ArgumentParser(description=self.description,
                                                add_help=False)
        config_parser.add_argument('-c', '--config',
                                   help='config file for setup.')
        config_parser.add_argument('--config-section',
                                   default=self.default_config_section,
                                   help='section of the config file for setup.')
        args, remaining_args = config_parser.parse_known_args()

        # Full parser
        parser = argparse.ArgumentParser(parents=[config_parser])
        self._setup_base_arguments(parser)
        self.setup_arguments(parser)

        # Read defaults from config file
        if args.config:
            cp = ConfigParser.RawConfigParser()
            with open(args.config) as fp:
                cp.readfp(fp)
            config_items = cp.items(args.config_section)

            valid_options = [option_string
                             for action in parser._actions
                             for option_string in action.option_strings]

            for option, value in config_items:
                option_string = '--%s' % option
                if option_string in valid_options:
                    remaining_args.extend([option_string, value])

        self.args = parser.parse_args(remaining_args)

    def _setup_base_arguments(self, parser):
        parser.add_argument('--logging-config',
                            dest='logging_config',
                            help='Optional config file for logging.'
                                 ' Default to config_uri')
        parser.add_argument('--verbose',
                            dest='logging_level',
                            default=logging.WARNING,
                            action='store_const',
                            const=logging.INFO)
        parser.add_argument('--debug',
                            dest='logging_level',
                            default=logging.WARNING,
                            action='store_const',
                            const=logging.DEBUG)

    def _setup_logging(self):
        if self.args.logging_config:
            logging.config.fileConfig(self.args.logging_config)
        elif self.args.config:
            logging.config.fileConfig(self.args.config)
        else:
            logging.basicConfig(level=self.args.logging_level)

    def _run(self):
        logging.debug('Run command with args: %s', self.args)
        try:
            self.run()
        except KeyboardInterrupt:
            sys.exit(1)


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
