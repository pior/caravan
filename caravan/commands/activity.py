import logging

from caravan import Activity
from caravan.commands.base import BaseCommand
from caravan.commands import ClassesLoaderFromModule
from caravan.swf import register_activity, get_connection
from caravan.workers.activity import Worker

log = logging.getLogger(__name__)


class Command(BaseCommand):

    description = 'Activity worker'

    def setup_arguments(self, parser):
        parser.add_argument('-m', '--modules',
                            type=ClassesLoaderFromModule(Activity),
                            nargs='+',
                            required=True)
        parser.add_argument('-d', '--domain',
                            required=True)
        parser.add_argument('-t', '--task-list',
                            required=True)
        parser.add_argument('--register-activities', action='store_true')

    def run(self):
        connection = get_connection()
        activities = [a for module in self.args.modules for a in module]

        if self.args.register_activities:
            log.info("Registering activity types")
            for activity in activities:
                created = register_activity(connection=connection,
                                            domain=self.args.domain,
                                            activity=activity)
                if created:
                    log.info("Activity type %s(%s): registered.",
                             activity.name, activity.version)
                else:
                    log.info("Activity type %s(%s): already registered.",
                             activity.name, activity.version)

        log.info("Start activity worker...")
        worker = Worker(connection=connection,
                        domain=self.args.domain,
                        task_list=self.args.task_list,
                        entities=activities)

        while True:
            try:
                worker.run()
            except Exception:  # Doesn't catch KeyboardInterrupt
                log.exception("Decider crashed!")
