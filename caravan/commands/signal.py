import sys

from botocore.exceptions import ClientError

from caravan.swf import get_swf_connection, is_response_success
from caravan.commands import BaseCommand


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
        connection = get_swf_connection()

        callargs = {}
        if self.args.input:
            callargs['input'] = self.args.input
        if self.args.run_id:
            callargs['runId'] = self.args.run_id

        try:
            response = connection.signal_workflow_execution(
                domain=self.args.domain,
                workflowId=self.args.id,
                signalName=self.args.signal,
                **callargs
                )
        except ClientError as err:
            sys.exit(err)
        else:
            if is_response_success(response):
                print 'Signal successfully sent'
            else:
                sys.exit('Error: %s' % response)
