import unittest
import json

import httpretty
from abduct import captured, out, err
from freezegun import freeze_time

from caravan.commands.list import Command


httpretty.HTTPretty.allow_net_connect = False


def httpretty_register():
    headers = {
        'x-amzn-RequestId': 'd68969c7-3f0d-11e1-9b11-7182192d0b57',
        }
    body = """
        { "executionInfos": [
                { "cancelRequested": false,
                  "execution": {
                    "runId": "f5ebbac6-941c-4342-ad69-dfd2f8be6689",
                    "workflowId": "20110927-T-1"
                  },
                  "executionStatus": "OPEN",
                  "startTimestamp": 1326585031.619,
                  "tagList": [
                    "music purchase", "digital", "ricoh-the-dog"
                  ],
                  "workflowType": {
                    "name": "customerOrderWorkflow",
                    "version": "1.0"
                  }
                } ]
            }"""
    httpretty.register_uri(httpretty.POST,
                           "https://swf.us-east-1.amazonaws.com/",
                           content_type='application/json',
                           adding_headers=headers,
                           body=body)


def run_command(additional_args):
    httpretty_register()

    args = ['-d', 'DOMAIN']
    args += additional_args
    with captured(out(), err()) as (stdout, stderr):
        Command.main(args=args)

    return stdout, stderr


class Test(unittest.TestCase):

    @freeze_time("2015-01-01")
    @httpretty.activate
    def test_nominal(self):
        httpretty_register()
        stdout, stderr = run_command([])
        request = httpretty.last_request()

        self.assertEqual(request.headers.get('x-amz-target'),
                         'SimpleWorkflowService.ListOpenWorkflowExecutions')

        expected = {
            "domain": "DOMAIN",
            'startTimeFilter': {
                'latestDate': 1420070400,
                'oldestDate': 1419984000
                }
            }
        self.assertEqual(json.loads(request.body), expected)

        self.assertIn('.', stdout.getvalue())

    @freeze_time("2015-01-01")
    @httpretty.activate
    def test_parameter_type_filter(self):
        httpretty_register()
        run_command(['-n', 'NAME', '-v', 'VERSION'])
        request = httpretty.last_request()

        expected = {
            "domain": "DOMAIN",
            'startTimeFilter': {
                'latestDate': 1420070400,
                'oldestDate': 1419984000
                },
            'typeFilter': {'name': 'NAME', 'version': 'VERSION'}
            }
        self.assertEqual(json.loads(request.body), expected)

    @freeze_time("2015-01-01")
    @httpretty.activate
    def test_parameter_tag_filter(self):
        httpretty_register()
        run_command(['--tag', 'TAG'])
        request = httpretty.last_request()

        expected = {
            "domain": "DOMAIN",
            'startTimeFilter': {
                'latestDate': 1420070400,
                'oldestDate': 1419984000
                },
            'tagFilter': {'tag': 'TAG'},
            }
        self.assertEqual(json.loads(request.body), expected)

    @freeze_time("2015-01-01")
    @httpretty.activate
    def test_parameter_id_filter(self):
        httpretty_register()
        run_command(['--id', 'ID'])
        request = httpretty.last_request()

        expected = {
            "domain": "DOMAIN",
            'startTimeFilter': {
                'latestDate': 1420070400,
                'oldestDate': 1419984000
                },
            'executionFilter': {'workflowId': 'ID'},
            }
        self.assertEqual(json.loads(request.body), expected)
