import logging
import pprint

from caravan.workers import get_default_identity
from caravan.models import DecisionTask

log = logging.getLogger(__name__)


class Worker(object):

    def __init__(self, connection, domain, task_list, workflows):
        self.conn = connection
        self.domain = domain
        self.task_list = task_list
        self.workflows = {w.name: w for w in workflows}
        self.identity = get_default_identity()

    def poll_swf(self):
        """Poll SWF for a decision task. Only return once actually get one."""
        task_list = dict(name=self.task_list)

        while True:
            resp = self.conn.poll_for_decision_task(domain=self.domain,
                                                    taskList=task_list,
                                                    identity=self.identity)

            task_token = resp.get('taskToken')
            if task_token:
                next_page_token = resp.get('nextPageToken')
                while next_page_token:
                    page = self.conn.poll_for_decision_task(
                        domain=self.domain,
                        taskList=task_list,
                        identity=self.identity,
                        nextPageToken=next_page_token)
                    next_page_token = page.get('nextPageToken')
                    resp['events'].extend(page['events'])

                return resp

    def run(self):
        log.info('Polling for decision task...')
        data = self.poll_swf()
        try:
            task = DecisionTask(data)
        except Exception as exc:
            log.error('Failed to prepare decision task: %s\nData:\n%s',
                      exc, pprint.pformat(data))
            raise

        log.info('Build decisions for task: %s', task)
        self.decide(task)

        log.info('Respond with decisions: %s', task.decisions)
        self.conn.respond_decision_task_completed(
            taskToken=task.token, decisions=task.decisions)

    def decide(self, task):
        workflow = self.workflows.get(task.workflow_type)
        if workflow:
            log.info('Run Workflow %s...', workflow)
            workflow().decide()
        else:
            log.warning('Unknown workflow %s', task.workflow_type)
            task.add_decision('FailWorkflowExecution',
                              reason='Unkown workflow type',
                              details='Workflow %s' % task.workflow_type)
