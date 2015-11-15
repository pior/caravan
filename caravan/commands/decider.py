import logging

from botocore.exceptions import ClientError

from caravan import Workflow
from caravan.commands.base import BaseCommand
from caravan.commands import ClassesLoaderFromModule, get_swf_connection
from caravan.workers.decider import Worker


log = logging.getLogger(__name__)


class Command(BaseCommand):

    description = 'Decider worker'

    def setup_arguments(self, parser):
        parser.add_argument('-m', '--modules',
                            type=ClassesLoaderFromModule(Workflow),
                            nargs='+',
                            required=True)
        parser.add_argument('-d', '--domain',
                            required=True)
        parser.add_argument('-t', '--task-list',
                            required=True)
        parser.add_argument('--register-workflows', action='store_true')

    def run(self):
        connection = get_swf_connection()
        workflows = [w for module in self.args.modules for w in module]

        if self.args.register_workflows:
            log.info("Registering workflow types")
            for workflow in workflows:
                created = register_workflow(connection=connection,
                                            domain=self.args.domain,
                                            workflow=workflow)
                if created:
                    log.info("Workflow type %s: registered.", workflow.name)
                else:
                    log.info("Workflow type %s: already registered.",
                             workflow.name)

        log.info("Start decider worker...")
        worker = Worker(connection=connection,
                        domain=self.args.domain,
                        task_list=self.args.task_list,
                        workflows=workflows)

        while True:
            try:
                worker.run()
            except Exception:  # Doesn't catch KeyboardInterrupt
                log.exception("Decider crashed!")


def register_workflow(connection, domain, workflow):
    args = dict([('default%s' % k, v) for k, v in workflow.defaults.items()])
    if 'defaultTaskList' in args:
        args['defaultTaskList'] = {'name': args['defaultTaskList']}
    description = getattr(workflow, 'description', None)
    if description:
        args['description'] = description

    try:
        connection.register_workflow_type(
            domain=domain,
            name=workflow.name,
            version=workflow.version,
            **args
            )

    except ClientError as err:
        error_code = err.response['Error']['Code']
        if error_code == 'TypeAlreadyExistsFault':
            return False  # Ignore this error
        raise

    return True
