import unittest
import json

import httpretty
from abduct import captured, out, err

from caravan.commands.terminate import Command


def httpretty_register():
    headers = {
        'x-amzn-RequestId': 'd68969c7-3f0d-11e1-9b11-7182192d0b57',
        }
    body = '{"runId": "1e536162-f1ea-48b0-85f3-aade88eef2f7"}'
    httpretty.register_uri(httpretty.POST,
                           "https://swf.us-east-1.amazonaws.com/",
                           content_type='application/json',
                           adding_headers=headers,
                           body=body)


def run_command(additional_args):
    httpretty_register()

    args = ['-d', 'DOMAIN', '-i', 'ID']
    args += additional_args
    with captured(out(), err()) as (stdout, stderr):
        Command.main(args=args)

    return stdout, stderr


class Test(unittest.TestCase):

    @httpretty.activate
    def test_nominal(self):
        httpretty_register()
        stdout, stderr = run_command([])
        request = httpretty.last_request()

        self.assertEqual(request.headers.get('x-amz-target'),
                         'SimpleWorkflowService.TerminateWorkflowExecution')

        expected = {
            "domain": "DOMAIN",
            "workflowId": "ID",
            }
        self.assertEqual(json.loads(request.body), expected)

        self.assertIn('Execution terminated.', stdout.getvalue())

    @httpretty.activate
    def test_parameter_run_id(self):
        httpretty_register()
        run_command(['--run-id', 'RUNID'])
        request = httpretty.last_request()

        expected = {
            "domain": "DOMAIN",
            "runId": 'RUNID',
            "workflowId": "ID",
            }
        self.assertEqual(json.loads(request.body), expected)

    @httpretty.activate
    def test_parameter_reason(self):
        httpretty_register()
        run_command(['--reason', 'REASON'])
        request = httpretty.last_request()

        expected = {
            "domain": "DOMAIN",
            "reason": 'REASON',
            "workflowId": "ID",
            }
        self.assertEqual(json.loads(request.body), expected)

    @httpretty.activate
    def test_parameter_details(self):
        httpretty_register()
        run_command(['--details', 'DETAILS'])
        request = httpretty.last_request()

        expected = {
            "domain": "DOMAIN",
            "details": 'DETAILS',
            "workflowId": "ID",
            }
        self.assertEqual(json.loads(request.body), expected)

    @httpretty.activate
    def test_parameter_child_policy(self):
        test_policy = Command.CHILD_POLICIES[0]

        httpretty_register()
        run_command(['--child-policy', test_policy])
        request = httpretty.last_request()

        expected = {
            "domain": "DOMAIN",
            "childPolicy": test_policy,
            "workflowId": "ID",
            }
        self.assertEqual(json.loads(request.body), expected)
