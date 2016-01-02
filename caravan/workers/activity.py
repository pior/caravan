import logging

from botocore.exceptions import ClientError

from caravan.workers import BaseWorker
from caravan.models.activity_task import ActivityTask, ActivityTaskFailure

log = logging.getLogger(__name__)


class Worker(BaseWorker):

    def poll(self):
        task_list = {'name': self.task_list}
        resp = self.conn.poll_for_activity_task(domain=self.domain,
                                                taskList=task_list,
                                                identity=self.identity)
        if 'taskToken' not in resp:
            return  # Polling timed out.

        return ActivityTask(resp)

    def run_task(self, task):
        activity_key = (task.activity_name, task.activity_version)
        activity_class = self.entities.get(activity_key)

        if not activity_class:
            log.warning('Unknown activity %s', task)
            return

        log.info('Running %r...', activity_class)
        try:
            activity_class(task)._run()
        except ActivityTaskFailure as exc:
            self.respond_failed(task, reason=exc.reason, details=exc.details)
        except Exception as exc:
            details = 'Exception %s: %s' % (type(exc), exc)
            self.respond_failed(task, reason='unknown_error', details=details)
        else:
            self.respond_completed(task)

    def respond_failed(self, task, reason, details):
        log.info('Respond task failed: %s (%s)', reason, details)
        try:
            self.conn.respond_activity_task_failed(taskToken=task.task_token,
                                                   reason=reason,
                                                   details=details)
        except ClientError as exc:
            log.error('respond_activity_task_failed failed for %s: %s\n%s',
                      task, exc.message, exc.response)
        except Exception as exc:
            log.error('respond_activity_task_failed failed for %s: %s',
                      task, exc)

    def respond_completed(self, task):
        log.info('Respond task complete: %s', task.result)
        args = {}
        if task.result is not None:
            args['result'] = task.result

        try:
            self.conn.respond_activity_task_completed(taskToken=task.task_token,
                                                      **args)
        except ClientError as exc:
            log.error('respond_activity_task_completed failed for %s: %s\n%s',
                      task, exc.message, exc.response)
        except Exception as exc:
            log.error('respond_activity_task_completed failed for %s: %s',
                      task, exc)
