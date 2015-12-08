import json
import unittest

import httpretty
from abduct import captured, out, err

from caravan.tests.util import mock_args
from caravan.commands.signal import Command


class Test(unittest.TestCase):

    @httpretty.activate
    def test_nominal(self):
        args = ['-d', 'DOMAIN', '-i', 'ID', '-s', 'SIG']

        headers = {
            'x-amzn-RequestId': 'd68969c7-3f0d-11e1-9b11-7182192d0b57',
            }
        httpretty.register_uri(httpretty.POST,
                               "https://swf.us-east-1.amazonaws.com/",
                               content_type='application/json',
                               adding_headers=headers,
                               body='')

        with captured(out(), err()) as (stdout, stderr):
            with mock_args(args):
                Command.main()

        request = httpretty.last_request()
        self.assertEqual(request.headers.get('x-amz-target'),
                         'SimpleWorkflowService.SignalWorkflowExecution')

        expected = {
            "domain": "DOMAIN",
            "workflowId": "ID",
            "signalName": "SIG"
            }
        self.assertEqual(json.loads(request.parsed_body), expected)

        self.assertIn('Signal sent.', stdout.getvalue())
