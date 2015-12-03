import unittest
import json

import httpretty
from abduct import captured, out, err

from caravan.commands.start import Command


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

    args = ['-d', 'DOMAIN', '-n', 'NAME', '-v', 'VERSION', '-i', 'ID']
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
                         'SimpleWorkflowService.StartWorkflowExecution')

        expected = {
            "domain": "DOMAIN",
            "workflowType": {"version": "VERSION", "name": "NAME"},
            "workflowId": "ID",
            }
        self.assertEqual(json.loads(request.parsed_body), expected)

        self.assertIn('Execution started.', stdout.getvalue())
        self.assertIn('1e536162-f1ea-48b0-85f3-aade88eef2f7',
                      stdout.getvalue())

    @httpretty.activate
    def test_parameter_task_list(self):
        httpretty_register()
        run_command(['-t', 'TASKLISTNAME'])
        request = httpretty.last_request()

        expected = {
            "domain": "DOMAIN",
            "taskList": {"name": "TASKLISTNAME"},
            "workflowId": "ID",
            "workflowType": {"version": "VERSION", "name": "NAME"},
            }
        self.assertEqual(json.loads(request.parsed_body), expected)

    @httpretty.activate
    def test_parameter_tag(self):
        httpretty_register()
        run_command(['--tag', 'TAG'])
        request = httpretty.last_request()

        expected = {
            "domain": "DOMAIN",
            "workflowType": {"version": "VERSION", "name": "NAME"},
            "workflowId": "ID",
            "tagList": ["TAG"],
            }
        self.assertEqual(json.loads(request.parsed_body), expected)

    @httpretty.activate
    def test_parameter_tag_two(self):
        httpretty_register()
        run_command(['--tag', 'TAG1 TAG2'])
        request = httpretty.last_request()

        expected = {
            "domain": "DOMAIN",
            "workflowType": {"version": "VERSION", "name": "NAME"},
            "workflowId": "ID",
            "tagList": ["TAG1", "TAG2"]
            }
        self.assertEqual(json.loads(request.parsed_body), expected)

    @httpretty.activate
    def test_parameter_input(self):
        httpretty_register()
        run_command(['--input', 'INPUT'])
        request = httpretty.last_request()

        expected = {
            "input": "INPUT",
            "domain": "DOMAIN",
            "workflowType": {"version": "VERSION", "name": "NAME"},
            "workflowId": "ID"
            }
        self.assertEqual(json.loads(request.parsed_body), expected)

    @httpretty.activate
    def test_parameter_execution_timeout(self):
        httpretty_register()
        run_command(['--execution-timeout', '60'])
        request = httpretty.last_request()

        expected = {
            "domain": "DOMAIN",
            "workflowType": {"version": "VERSION", "name": "NAME"},
            "workflowId": "ID",
            "executionStartToCloseTimeout": "60",
            }
        self.assertEqual(json.loads(request.parsed_body), expected)

    @httpretty.activate
    def test_parameter_task_timeout(self):
        httpretty_register()
        run_command(['--task-timeout', '60'])
        request = httpretty.last_request()

        expected = {
            "domain": "DOMAIN",
            "workflowType": {"version": "VERSION", "name": "NAME"},
            "workflowId": "ID",
            "taskStartToCloseTimeout": "60",
            }
        self.assertEqual(json.loads(request.parsed_body), expected)

    @httpretty.activate
    def test_parameter_child_policy(self):
        test_policy = Command.CHILD_POLICIES[0]
        httpretty_register()
        run_command(['--child-policy', test_policy])
        request = httpretty.last_request()

        Command.CHILD_POLICIES[0]
        expected = {
            "domain": "DOMAIN",
            "workflowType": {"version": "VERSION", "name": "NAME"},
            "workflowId": "ID",
            "childPolicy": test_policy,
            }
        self.assertEqual(json.loads(request.parsed_body), expected)

    @httpretty.activate
    def test_parameter_lambda_role(self):
        httpretty_register()
        run_command(['--lambda-role', 'ROLE'])
        request = httpretty.last_request()

        Command.CHILD_POLICIES[0]
        expected = {
            "domain": "DOMAIN",
            "workflowType": {"version": "VERSION", "name": "NAME"},
            "workflowId": "ID",
            "lambdaRole": 'ROLE',
            }
        self.assertEqual(json.loads(request.parsed_body), expected)
