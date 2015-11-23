from caravan.commands import run_swf_command
from caravan.commands.base import BaseCommand


class Command(BaseCommand):

    description = 'Start a workflow execution'

    def setup_arguments(self, parser):
        parser.add_argument('-d', '--domain', required=True)
        parser.add_argument('-i', '--id', required=True)
        parser.add_argument('-n', '--name', required=True)
        parser.add_argument('-v', '--version', required=True)
        parser.add_argument('-t', '--task-list')

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
            help='The maximum total duration for this workflow execution '
                 '(seconds)')
        parser.add_argument(
            '--task-timeout',
            help='The maximum duration of decision tasks (seconds)')
        parser.add_argument(
            '--child-policy',
            choices=self.CHILD_POLICIES,
            help='Policy to use for the child executions of this execution')
        parser.add_argument(
            '--lambda-role',
            help='ARN of an IAM role that authorizes SWF to invoke Lambda '
                 'functions')

    def run(self):
        workflow_type = {'name': self.args.name, 'version': self.args.version}

        if self.args.tag_list:
            tag_list = self.args.tag_list.split()
        else:
            tag_list = None

        response = run_swf_command(
            'start_workflow_execution',
            domain=self.args.domain,
            workflowId=self.args.id,
            workflowType=workflow_type,
            input=self.args.input,
            task_list=self.args.task_list,
            tagList=tag_list,
            executionStartToCloseTimeout=self.args.execution_timeout,
            taskStartToCloseTimeout=self.args.task_timeout,
            childPolicy=self.args.child_policy,
            lambdaRole=self.args.lambda_role,
            )

        return 'Execution started. RunId: %s' % response['runId']
