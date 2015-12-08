import unittest
import json

import httpretty
from abduct import captured, out, err

from caravan.tests.util import mock_args
from caravan.commands.domain_list import Command


def httpretty_register():
    headers = {
        'x-amzn-RequestId': 'd68969c7-3f0d-11e1-9b11-7182192d0b57',
        }
    body = """
        {"domainInfos":
          [
            {"description": "music", "name": "867530901", "status": "REGISTERED"},
            {"description": "music", "name": "867530902", "status": "REGISTERED"},
            {"description": "", "name": "Demo", "status": "REGISTERED"}
          ]
        } """
    httpretty.register_uri(httpretty.POST,
                           "https://swf.us-east-1.amazonaws.com/",
                           content_type='application/json',
                           adding_headers=headers,
                           body=body)


def run_command(additional_args):
    httpretty_register()

    args = []
    args += additional_args
    with captured(out(), err()) as (stdout, stderr):
        with mock_args(args):
            Command.main()

    return stdout, stderr


class Test(unittest.TestCase):

    @httpretty.activate
    def test_nominal(self):
        httpretty_register()
        stdout, stderr = run_command([])
        request = httpretty.last_request()

        self.assertEqual(request.headers.get('x-amz-target'),
                         'SimpleWorkflowService.ListDomains')

        expected = {
            "registrationStatus": "REGISTERED",
            }
        self.assertEqual(json.loads(request.parsed_body), expected)

        self.assertIn('867530901', stdout.getvalue())
        self.assertIn('music', stdout.getvalue())

    @httpretty.activate
    def test_registration_status(self):
        httpretty_register()
        stdout, stderr = run_command(['--deprecated'])
        request = httpretty.last_request()

        expected = {
            "registrationStatus": "DEPRECATED",
            }
        self.assertEqual(json.loads(request.parsed_body), expected)
