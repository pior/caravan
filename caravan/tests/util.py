import os
import tempfile

import mock


class InTempDir(object):

    def __enter__(self):
        self._tmpdir = os.path.realpath(tempfile.mkdtemp())
        self._pwd = os.getcwd()
        os.chdir(self._tmpdir)
        return self

    def __exit__(self, *args):
        os.chdir(self._pwd)


def mock_args(args):
    return mock.patch('sys.argv', ['PROG'] + args)
