import logging
import pprint

from botocore.exceptions import ClientError

from caravan.workers import get_default_identity
from caravan.models.decision import DecisionTask, DecisionDone

log = logging.getLogger(__name__)


class Worker(object):

    def __init__(self, connection, domain, task_list, workflows):
        self.conn = connection
        self.domain = domain
        self.task_list = task_list
        self.Workflows = {(w.name, w.version): w for w in workflows}
        self.identity = get_default_identity()

    def run(self):
        log.info('Waiting for a decision task...')
        task = self.poll()
        if task:
            log.info('Got a %r', task)
            self.decide(task)

            log.info('Respond with decisions: %s', task.decisions)
            self.respond_decision(task)

    def poll(self):
        task_list = dict(name=self.task_list)

        resp = self.conn.poll_for_decision_task(domain=self.domain,
                                                taskList=task_list,
                                                identity=self.identity)
        if 'taskToken' not in resp:
            return  # Polling timed out.

        next_page_token = resp.get('nextPageToken')
        while next_page_token:
            page = self.conn.poll_for_decision_task(
                domain=self.domain,
                taskList=task_list,
                identity=self.identity,
                nextPageToken=next_page_token)
            next_page_token = page.get('nextPageToken')
            resp['events'].extend(page['events'])

        return DecisionTask(resp)

    def decide(self, task):
        workflow_key = (task.workflow_type, task.workflow_version)
        Workflow = self.Workflows.get(workflow_key)

        if not Workflow:
            log.warning('Unknown workflow %s', task)
            return

        workflow = Workflow(task)

        log.info('Running %r...', workflow)

        try:
            workflow.run()
        except DecisionDone as done:
            log.info(str(done))

    def respond_decision(self, task):
        try:
            self.conn.respond_decision_task_completed(
                taskToken=task.token,
                decisions=task.decisions)
        except ClientError as exc:
            log.error('Decision response failed for %s: %s\n%s',
                      task, exc.message, exc.response)
        except Exception as exc:
            log.error('Decision response failed for %s: %s', task, exc)
