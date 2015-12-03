import unittest
import logging

from abduct import captured, out, err

from caravan.tests.util import InTempDir
from caravan.commands.base import BaseCommand


class TestCommand(BaseCommand):

    description = 'DESCRIPTION TEST'

    def setup_arguments(self, parser):
        parser.add_argument('-o', '--opt')

    def run(self):
        arguments = self.args.__dict__.items()
        lines = ['%s=%s' % (k, v) for k, v in arguments]
        lines.append('EndOfOutput')
        return '\n'.join(lines)


class RequiredArgCommand(TestCommand):

    def setup_arguments(self, parser):
        parser.add_argument('-r', '--req', required=True)
        parser.add_argument('-o', '--opt')


class KeyboardInterruptCommand(TestCommand):

    def run(self):
        raise KeyboardInterrupt()


CONFIG_FILE_DATA = """
[caravan]
req = REQFILE
opt = OPTFILE
"""

LOGGING_CONFIG_FILE_DATA = """
[loggers]
keys = root

[logger_root]
level = DEBUG
handlers = console

[handlers]
keys = console

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = DEBUG
formatter = console

[formatters]
keys = console

[formatter_console]
format = %(message)s
"""


class Test(unittest.TestCase):

    def test_args_optional(self):
        with captured(out(), err()) as (stdout, stderr):
            response = TestCommand.main(args=[])
        self.assertIn('opt=None', response)

        with captured(out(), err()) as (stdout, stderr):
            response = TestCommand.main(args=['--opt', 'OPT'])
        self.assertIn('opt=OPT', response)

    def test_args_missing(self):
        with captured(out(), err()) as (stdout, stderr):
            with self.assertRaises(SystemExit):
                RequiredArgCommand.main(args=[])

        # Py2 and Py3 argparse have different messages
        self.assertIn('error: ', stderr.getvalue())
        self.assertIn('-r/--req', stderr.getvalue())
        self.assertIn('required', stderr.getvalue())

    def test_args_logging_level(self):
        with captured(out(), err()) as (stdout, stderr):
            response = TestCommand.main(args=[])
        self.assertIn('logging_level=%s' % logging.WARNING, response)

        with captured(out(), err()) as (stdout, stderr):
            response = TestCommand.main(args=['--verbose'])
        self.assertIn('logging_level=%s' % logging.INFO, response)

        with captured(out(), err()) as (stdout, stderr):
            response = TestCommand.main(args=['--debug'])
        self.assertIn('logging_level=%s' % logging.DEBUG, response)

    def test_config(self):
        with InTempDir():
            with open('config.conf', 'w') as fd:
                fd.write(CONFIG_FILE_DATA)

            args = ['--config', 'config.conf']
            with captured(out(), err()) as (stdout, stderr):
                TestCommand.main(args=args)

        self.assertIn('EndOfOutput', stdout.getvalue())

    def test_args_logging_config(self):
        with InTempDir():
            with open('logging.conf', 'w') as fd:
                fd.write(LOGGING_CONFIG_FILE_DATA)

            args = ['--logging-config', 'logging.conf']
            with captured(out(), err()) as (stdout, stderr):
                TestCommand.main(args=args)

        self.assertIn('EndOfOutput', stdout.getvalue())

    def test_args_help(self):
        with captured(out(), err()) as (stdout, stderr):
            with self.assertRaises(SystemExit):
                TestCommand.main(args=['--help'])
        self.assertIn(TestCommand.description, stdout.getvalue())

    def test_keyboard_interrupt(self):
        with captured(out(), err()) as (stdout, stderr):
            with self.assertRaises(SystemExit) as exc:
                KeyboardInterruptCommand.main(args=[])
        self.assertEqual(str(exc.exception), '1')
