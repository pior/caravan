import logging

from botocore.exceptions import ClientError

from caravan.workers import BaseWorker
from caravan.models.decision_task import (DecisionTask,
                                          DecisionDone,
                                          WorkflowFailure)

log = logging.getLogger(__name__)


class Worker(BaseWorker):

    def poll(self):
        task_list = {'name': self.task_list}
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
            resp['events'].extend(page['events'])
            next_page_token = page.get('nextPageToken')

        return DecisionTask(resp)

    def run_task(self, task):
        workflow_key = (task.workflow_type, task.workflow_version)
        workflow_class = self.entities.get(workflow_key)

        if not workflow_class:
            log.warning('Unknown workflow %s', task)
            return

        log.info('Running %r...', workflow_class)
        try:
            workflow_class(task).run()
        except DecisionDone as done:
            log.info(str(done))
        except WorkflowFailure as failure:
            task.add_decision('FailWorkflowExecution',
                              reason=failure.reason,
                              details=failure.details)

        log.info('Respond with decisions: %s', task.decisions)
        self.respond_decision(task)

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
