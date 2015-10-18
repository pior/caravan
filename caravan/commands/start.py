import sys
import argparse

import botocore.exceptions

from caravan.commands import get_swf_connection, is_response_success


def main():
    parser = argparse.ArgumentParser(description='Start a workflow execution')
    parser.add_argument('-d', '--domain', required=True)
    parser.add_argument('-i', '--id', required=True)
    parser.add_argument('-n', '--name', required=True)
    parser.add_argument('-v', '--version', required=True)
    parser.add_argument('--input', help='Raw input data for this execution')
    parser.add_argument('-t', '--task-list')
    parser.add_argument(
        '--tag-list',
        help='List of tags to associate with the workflow execution',
        metavar='"tag1 tag2 ..."')
    parser.add_argument(
        '--execution-timeout',
        help='The maximum total duration for this workflow execution (seconds)')
    parser.add_argument(
        '--task-timeout',
        help='The maximum duration of decision tasks (seconds)')
    parser.add_argument(
        '--child-policy',
        help='Policy to use for the child executions of this execution')
    parser.add_argument(
        '--lambda-role',
        help='ARN of an IAM role that authorizes SWF to invoke Lambda functions')
    args = parser.parse_args()

    connection = get_swf_connection()

    callargs = {}
    if args.input:
        callargs['input'] = args.input
    if args.task_list:
        callargs['taskList'] = {'name': args.task_list}
    if args.tag_list:
        callargs['tagList'] = args.tag_list.split()
    if args.execution_timeout:
        callargs['executionStartToCloseTimeout'] = args.execution_timeout
    if args.task_timeout:
        callargs['taskStartToCloseTimeout'] = args.task_timeout
    if args.child_policy:
        callargs['childPolicy'] = args.child_policy
    if args.lambda_role:
        callargs['lambdaRole'] = args.lambda_role

    try:
        response = connection.start_workflow_execution(
            domain=args.domain,
            workflowId=args.id,
            workflowType={
                'name': args.name,
                'version': args.version
            },
            **callargs)
    except botocore.exceptions.ClientError as err:
        sys.exit(err)
    except KeyboardInterrupt:
        sys.exit(1)
    else:
        if is_response_success(response):
            print 'Workflow execution successfully created as RunId %s' % (
                response['runId'])
        else:
            print 'Response: %s' % response
