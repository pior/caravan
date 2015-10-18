import sys
import argparse
import logging

from caravan import Workflow
from caravan.commands import (
    ClassLoaderFromModule, get_swf_connection, setup_logging, register_workflow)
from caravan.workers.decider import Worker


def main():
    parser = argparse.ArgumentParser(description='Decider worker')
    parser.add_argument('-m', '--module',
                        dest='workflows',
                        type=ClassLoaderFromModule(Workflow),
                        required=True)
    parser.add_argument('-d', '--domain',
                        required=True)
    parser.add_argument('-t', '--task-list',
                        required=True)
    parser.add_argument('--register-workflows', action='store_true')
    args = parser.parse_args()

    setup_logging()
    log = logging.getLogger(__name__)

    connection = get_swf_connection()

    if args.register_workflows:
        log.info("Registering workflow types")
        for workflow in args.workflows:
            created = register_workflow(connection=connection,
                                        domain=args.domain,
                                        workflow=workflow)
            if created:
                log.info("Workflow type %s: registered.", workflow.name)
            else:
                log.info("Workflow type %s: already registered.", workflow.name)

    log.info("Start decider worker...")
    worker = Worker(connection=connection,
                    domain=args.domain,
                    task_list=args.task_list,
                    workflows=args.workflows)

    try:
        while True:
            worker.run()
    except KeyboardInterrupt:
        sys.exit(1)
