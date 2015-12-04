from caravan.commands import run_swf_command
from caravan.commands.base import BaseCommand


class Command(BaseCommand):

    description = 'List domains'

    def setup_arguments(self, parser):
        parser.add_argument('--deprecated',
                            dest='registration_status',
                            action='store_const',
                            const='DEPRECATED',
                            default='REGISTERED')

    def run(self):
        response = run_swf_command(
            'list_domains',
            registrationStatus=self.args.registration_status
            )

        return response['domainInfos']
