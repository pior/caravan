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


class TestUtilMixin(object):

    def assertIsSwfConnection(self, obj):
        # Boto3 client object are dynamically built type...
        self.assertEqual(obj.__class__.__name__, 'SWF')
        self.assertEqual(obj.__class__.__module__, 'botocore.client')

    def mock_args(self, args):
        return mock.patch('sys.argv', ['PROG'] + args)
