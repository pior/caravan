from caravan.commands import run_swf_command
from caravan.commands.base import BaseCommand


class Command(BaseCommand):

    description = 'Signal a workflow execution'

    def setup_arguments(self, parser):
        parser.add_argument('-d', '--domain', required=True)
        parser.add_argument('-i', '--id', required=True)
        parser.add_argument('--run-id')
        parser.add_argument('-s', '--signal', required=True)
        parser.add_argument(
            '--input',
            help='Raw input data for this signal',
            metavar='"<Some data>"')

    def run(self):
        run_swf_command(
            'signal_workflow_execution',
            domain=self.args.domain,
            workflowId=self.args.id,
            signalName=self.args.signal,
            runId=self.args.run_id,
            input=self.args.input,
            )
