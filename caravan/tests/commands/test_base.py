import logging

import pytest

from caravan.commands.base import BaseCommand


class TestCommand(BaseCommand):

    description = 'DESCRIPTION TEST'

    def setup_arguments(self, parser):
        parser.add_argument('-r', '--req', required=True)
        parser.add_argument('-o', '--opt')

    def run(self):
        print 'req=%s' % self.args.req
        print 'opt=%s' % self.args.opt
        print 'lvl=%s' % self.args.logging_level


def test_args(mocker, capsys):
    mocker.patch('sys.argv', ['PROG', '--req', 'REQ'])
    TestCommand.main()
    out, _ = capsys.readouterr()
    assert 'req=REQ' in out
    assert 'opt=None' in out

    mocker.patch('sys.argv', ['PROG', '--req', 'REQ', '--opt', 'OPT'])
    TestCommand.main()
    out, _ = capsys.readouterr()
    assert 'req=REQ' in out
    assert 'opt=OPT' in out


def test_args_logging_level(mocker, capsys):
    mocker.patch('sys.argv', ['PROG', '--req', 'REQ'])
    TestCommand.main()
    out, _ = capsys.readouterr()
    assert 'lvl=%s' % logging.WARNING in out

    mocker.patch('sys.argv', ['PROG', '--req', 'REQ', '--verbose'])
    TestCommand.main()
    out, _ = capsys.readouterr()
    assert 'lvl=%s' % logging.INFO in out

    mocker.patch('sys.argv', ['PROG', '--req', 'REQ', '--debug'])
    TestCommand.main()
    out, _ = capsys.readouterr()
    assert 'lvl=%s' % logging.DEBUG in out


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


def test_args_logging_config(mocker, capsys, tmpdir):
    tmpdir.chdir()
    configfile = tmpdir.join('logging.conf')
    configfile.write(LOGGING_CONFIG_FILE_DATA)

    mocker.patch('sys.argv', ['PROG', '--req', 'REQ', '--logging-config',
                              'logging.conf'])
    TestCommand.main()


def test_args_missing(mocker, capsys):
    mocker.patch('sys.argv', ['PROG'])

    with pytest.raises(SystemExit):
        TestCommand.main()

    _, err = capsys.readouterr()
    assert 'PROG: error: argument -r/--req is required' in err


def test_args_help(mocker, capsys):
    mocker.patch('sys.argv', ['PROG', '--help'])

    with pytest.raises(SystemExit):
        TestCommand.main()

    out, _ = capsys.readouterr()
    assert TestCommand.description in out
