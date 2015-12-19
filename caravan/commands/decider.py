import logging

from caravan import Workflow
from caravan.commands.base import BaseCommand
from caravan.commands import ClassesLoaderFromModule
from caravan.swf import register_workflow, get_connection
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
        connection = get_connection()
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
