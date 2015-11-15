from caravan.commands import run_swf_command
from caravan.commands.base import BaseCommand


class Command(BaseCommand):

    description = 'Register a domain'
    default_config_section = 'caravan:domain'

    def setup_arguments(self, parser):
        parser.add_argument('-n', '--name', required=True)
        parser.add_argument(
            '--retention-days',
            dest='retention_days',
            required=True,
            help='Retention period for workflow execution')
        parser.add_argument('--description')

    def run(self):
        run_swf_command(
            'register_domain',
            name=self.args.name,
            workflowExecutionRetentionPeriodInDays=self.args.retention_days,
            description=self.args.description,
            )
