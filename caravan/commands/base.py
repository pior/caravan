import argparse
import ConfigParser
import logging
import logging.config
import sys

import six
from tabulate import tabulate


class BaseCommand(object):

    """Base class for command-line tools."""

    default_config_section = 'caravan'

    CHILD_POLICIES = [
        'TERMINATE',
        'REQUEST_CANCEL',
        'ABANDON',
        ]

    @classmethod
    def main(cls, args=None):
        """Setuptools console-script entrypoint"""
        cmd = cls()
        cmd._parse_args(args=args)
        cmd._setup_logging()
        response = cmd._run()
        output = cmd._handle_response(response)
        if output is not None:
            print output
        return response

    def _parse_args(self, args=None):
        # Config only parser
        config_parser = argparse.ArgumentParser(description=self.description,
                                                add_help=False)
        config_parser.add_argument('-c', '--config',
                                   help='config file for setup.')
        config_parser.add_argument('--config-section',
                                   default=self.default_config_section,
                                   help='section of the config file for '
                                        'setup.')
        config_args, remaining_args = config_parser.parse_known_args(args=args)

        # Full parser
        parser = argparse.ArgumentParser(description=self.description,
                                         parents=[config_parser])
        self._setup_base_arguments(parser)
        self.setup_arguments(parser)

        # Read defaults from config file
        if config_args.config:
            cp = ConfigParser.RawConfigParser()
            with open(config_args.config) as fp:
                cp.readfp(fp)
            config_items = cp.items(config_args.config_section)

            valid_options = [option_string
                             for action in parser._actions
                             for option_string in action.option_strings]
            nargs_options = {option_string: action.nargs
                             for action in parser._actions
                             for option_string in action.option_strings}

            for option, value in config_items:
                option_string = '--%s' % option

                if option_string in valid_options:
                    if nargs_options.get(option_string) == '+':
                        value = value.split()
                        option_args = [option_string] + value
                    else:
                        option_args = [option_string, value]
                    args.extend(option_args)

        self.args = parser.parse_args(args)

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
            try:
                logging.config.fileConfig(self.args.config)
            except ConfigParser.NoSectionError:
                pass
        else:
            logging.basicConfig(level=self.args.logging_level)

    def _run(self):
        logging.debug('Run command with args: %s', self.args)
        try:
            return self.run()
        except KeyboardInterrupt:
            sys.exit(1)

    def _handle_response(self, response):
        if response is None:
            return "Success."
        elif isinstance(response, six.string_types):
            return response
        elif isinstance(response, list):
            if len(response) == 0:
                return 'No results.'
            if hasattr(self, 'formatter'):
                response = map(self.formatter, response)
            return tabulate(response, headers='keys', tablefmt="plain")
