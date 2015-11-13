import sys

from botocore.exceptions import ClientError

from caravan.swf import get_swf_connection, is_response_success
from caravan.commands import BaseCommand


class Command(BaseCommand):

    description = 'Start a workflow execution'

    def setup_arguments(self, parser):
        parser.add_argument('-d', '--domain', required=True)
        parser.add_argument('-i', '--id', required=True)
        parser.add_argument('-n', '--name', required=True)
        parser.add_argument('-v', '--version', required=True)
        parser.add_argument('-t', '--task-list', required=True)

        parser.add_argument(
            '--input',
            help='Raw input data for this execution',
            metavar='"<Some data>"')
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

    def run(self):
        connection = get_swf_connection()

        callargs = {
            'taskList': {'name': self.args.task_list},
            }

        if self.args.input:
            callargs['input'] = self.args.input
        if self.args.tag_list:
            callargs['tagList'] = self.args.tag_list.split()
        if self.args.execution_timeout:
            callargs['executionStartToCloseTimeout'] = self.args.execution_timeout
        if self.args.task_timeout:
            callargs['taskStartToCloseTimeout'] = self.args.task_timeout
        if self.args.child_policy:
            callargs['childPolicy'] = self.args.child_policy
        if self.args.lambda_role:
            callargs['lambdaRole'] = self.args.lambda_role

        try:
            response = connection.start_workflow_execution(
                domain=self.args.domain,
                workflowId=self.args.id,
                workflowType={
                    'name': self.args.name,
                    'version': self.args.version
                    },
                **callargs)
        except ClientError as err:
            sys.exit(err)
        else:
            if is_response_success(response):
                print 'Workflow execution successfully created as RunId %s' % (
                    response['runId'])
            else:
                sys.exit('Error: %s' % response)
