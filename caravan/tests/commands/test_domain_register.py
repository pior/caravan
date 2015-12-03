import json
import unittest

import httpretty
from abduct import captured, out, err

from caravan.commands.domain_register import Command


httpretty.HTTPretty.allow_net_connect = False


class Test(unittest.TestCase):

    @httpretty.activate
    def test_nominal(self):
        args = ['--name', 'DOMAIN', '--retention-days', '10']

        headers = {
            'x-amzn-RequestId': 'd68969c7-3f0d-11e1-9b11-7182192d0b57',
            }
        httpretty.register_uri(httpretty.POST,
                               "https://swf.us-east-1.amazonaws.com/",
                               content_type='application/json',
                               adding_headers=headers,
                               body='')

        with captured(out(), err()) as (stdout, stderr):
            Command.main(args=args)

        request = httpretty.last_request()
        self.assertEqual(request.headers.get('x-amz-target'),
                         'SimpleWorkflowService.RegisterDomain')
        expected = {
            "name": "DOMAIN",
            "workflowExecutionRetentionPeriodInDays": "10"
            }
        self.assertEqual(json.loads(request.body), expected)

        self.assertIn('Success.', stdout.getvalue())
