class ActivityTaskFailure(Exception):

    def __init__(self, reason, details):
        self.reason = reason
        self.details = details
        super(ActivityTaskFailure, self).__init__('%s: %s' % (reason, details))


class ActivityTask(object):

    """An activity task."""

    def __init__(self, data):
        self.task_token = data['taskToken']
        self.activity_id = data['activityId']
        self.workflow_id = data['workflowExecution']['workflowId']
        self.workflow_run_id = data['workflowExecution']['runId']
        self.activity_name = data['activityType']['name']
        self.activity_version = data['activityType']['version']
        self.task_input = data.get('input')
        self.result = None

    def __repr__(self):
        return '<ActivityTask %s(%s) id=%s WorkflowId=%s>' % (
            self.activity_name,
            self.activity_version,
            self.activity_id,
            self.workflow_id)

    def fail(self, reason, details):
        raise ActivityTaskFailure(reason, details)

    def set_result(self, result):
        self.result = result
