import unittest


class TestException(unittest.TestCase):

    def test_decision_done(self):
        from caravan.models.decision import DecisionDone

        exc = DecisionDone('STUFF')
        self.assertEqual(str(exc), 'STUFF')

    def test_workflow_failure(self):
        from caravan.models.decision import WorkflowFailure

        exc = WorkflowFailure('REASON', 'DETAILS')

        self.assertEqual(str(exc), 'REASON (DETAILS)')
        self.assertEqual(exc.reason, 'REASON')
        self.assertEqual(exc.details, 'DETAILS')


EVENT_EXEC_STARTED_ATTRIBUTES = {
    "childPolicy": "string",
    "continuedExecutionRunId": "string",
    "executionStartToCloseTimeout": "string",
    "input": "string",
    "lambdaRole": "string",
    "parentInitiatedEventId": 1,
    "parentWorkflowExecution": {
        "runId": "string",
        "workflowId": "string"
    },
    "tagList": [
        "string"
    ],
    "taskList": {
        "name": "string"
    },
    "taskPriority": "string",
    "taskStartToCloseTimeout": "string",
    "workflowType": {
        "name": "string",
        "version": "string"
    },
}


class TestDecisionTask(unittest.TestCase):

    @property
    def decision_data(self):
        """Return a new copy of a DecisionTask test payload."""
        decision_data = {
            "events": [{
                "workflowExecutionStartedEventAttributes":
                EVENT_EXEC_STARTED_ATTRIBUTES,
                }],
            "nextPageToken": "NEXT_PAGE_TOKEN",
            "previousStartedEventId": 1,
            "startedEventId": 1,
            "taskToken": "TOKEN",
            "workflowExecution": {
                "runId": "RID",
                "workflowId": "WID"
                },
            "workflowType": {
                "name": "NAME",
                "version": "VERSION"
                },
            }
        return decision_data

    def test_nominal(self):
        from caravan.models.decision import DecisionTask

        task = DecisionTask(self.decision_data)

        expected = [{
            'attributes': EVENT_EXEC_STARTED_ATTRIBUTES
            }]
        self.assertEqual(task.events, expected)

        self.assertEqual(task.token, 'TOKEN')
        self.assertEqual(task.workflow_id, 'WID')
        self.assertEqual(task.run_id, 'RID')
        self.assertEqual(task.workflow_type, 'NAME')
        self.assertEqual(task.workflow_version, 'VERSION')

        self.assertEqual(task.decisions, [])

    def test_repr(self):
        from caravan.models.decision import DecisionTask

        task = DecisionTask(self.decision_data)
        self.assertEqual(repr(task),
                         '<DecisionTask NAME v=VERSION id=WID runId=RID>')

    def test_decision_done(self):
        pass

    def test_fail(self):
        pass

    def test_print_events(self):
        pass

    def test_add_decision(self):
        pass
