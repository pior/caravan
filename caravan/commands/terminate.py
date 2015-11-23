from caravan.commands import run_swf_command
from caravan.commands.base import BaseCommand


class Command(BaseCommand):

    description = 'Terminate a workflow execution'

    def setup_arguments(self, parser):
        parser.add_argument('-d', '--domain', required=True)
        parser.add_argument('-i', '--id', required=True)
        parser.add_argument('--run-id')
        parser.add_argument('--reason')
        parser.add_argument('--details')
        parser.add_argument('--child-policy', choices=self.CHILD_POLICIES)

    def run(self):
        run_swf_command(
            'terminate_workflow_execution',
            domain=self.args.domain,
            workflowId=self.args.id,
            runId=self.args.run_id,
            reason=self.args.reason,
            details=self.args.details,
            childPolicy=self.args.child_policy,
            )
        return 'Execution terminated.'
