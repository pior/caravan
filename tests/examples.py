import logging

from caravan import Workflow

log = logging.getLogger(__name__)


class Test1(Workflow):

    name = 'Test1'
    version = '1.3'
    defaults = {
        'ExecutionStartToCloseTimeout': '3600',
        'TaskStartToCloseTimeout': '10',
        'TaskList': 'default',
        'ChildPolicy': 'TERMINATE',
        }

    def decide(self, task):
        log.info("Inside %s workflow", self.name)
