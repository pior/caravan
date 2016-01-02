from caravan import Workflow, Activity


class TestWorkflow1(Workflow):

    name = 'Workflow1'


class TestWorkflow2(Workflow):

    name = 'Workflow2'


class TestActivity1(Activity):

    name = 'Activity1'
    version = '1'

    def run(self, input):
        return 'DONE'


class TestActivity2(Activity):

    name = 'Activity2'
    version = '2'

    def run(self, input):
        self.task.fail('REASON', 'DETAILS')


def make_activity_task_data(name='NAME', version='VERSION', input='INPUT'):
    data = {
        'taskToken': 'TASK_TOKEN',
        'activityId': 'ACTIVITY_ID',
        'startedEventId': 123,
        'workflowExecution': {
            'workflowId': 'WORKFLOW_ID',
            'runId': 'RUN_ID'
            },
        'activityType': {
            'name': name,
            'version': version,
            },
        }
    if input is not None:
        data['input'] = input
    return data
