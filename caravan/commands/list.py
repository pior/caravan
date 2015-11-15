import arrow

from caravan.commands import run_swf_command
from caravan.commands.base import BaseCommand


class Command(BaseCommand):

    description = 'List workflow executions'

    def setup_arguments(self, parser):
        present = arrow.utcnow()
        default_oldest = present.replace(days=-1)
        default_latest = present.clone()

        parser.add_argument('-d', '--domain', required=True)
        parser.add_argument('--oldest', default=default_oldest, type=arrow.get)
        parser.add_argument('--latest', default=default_latest, type=arrow.get)

        filter_group = parser.add_mutually_exclusive_group()
        type_group = filter_group.add_argument_group()
        type_group.add_argument('-n', '--name')
        type_group.add_argument('-v', '--version')
        filter_group.add_argument('--tag')
        filter_group.add_argument('--id')

    def run(self):
        time_filter = {
            'oldestDate': self.args.oldest.naive,
            'latestDate': self.args.latest.naive,
            }

        if self.args.name is not None:
            type_filter = {
                'name': self.args.name,
                }
            if self.args.version is not None:
                type_filter['version'] = self.args.version
        else:
            type_filter = None

        if self.args.tag is not None:
            tag_filter = {
                'tag': self.args.tag,
                }
        else:
            tag_filter = None

        if self.args.id is not None:
            execution_filter = {
                'workflowId': self.args.id,
                }
        else:
            execution_filter = None

        response = run_swf_command(
            'list_open_workflow_executions',
            domain=self.args.domain,
            startTimeFilter=time_filter,
            typeFilter=type_filter,
            tagFilter=tag_filter,
            executionFilter=execution_filter,
            )

        return response['executionInfos']

    def formatter(self, e):
        w = e['workflowType']
        return {
            'Start': arrow.get(e['startTimestamp']).humanize(),
            'Workflow Type': '%s(%s)' % (w['name'], w['version']),
            'Workflow Id': e['execution']['workflowId'],
            'Run Id': e['execution']['runId'],
            'Status': e['executionStatus'],
            }
