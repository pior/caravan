import unittest

from caravan.models.activity_task import ActivityTask, ActivityTaskFailure

from .. import fixtures


class Test(unittest.TestCase):

    def test_nominal(self):
        data = fixtures.make_activity_task_data()
        task = ActivityTask(data)
        self.assertEqual(task.task_token, 'TASK_TOKEN')
        self.assertEqual(task.activity_id, 'ACTIVITY_ID')
        self.assertEqual(task.workflow_id, 'WORKFLOW_ID')
        self.assertEqual(task.workflow_run_id, 'RUN_ID')
        self.assertEqual(task.activity_name, 'NAME')
        self.assertEqual(task.activity_version, 'VERSION')
        self.assertEqual(task.task_input, 'INPUT')

    def test_no_input(self):
        data = fixtures.make_activity_task_data(input=None)
        task = ActivityTask(data)
        self.assertEqual(task.task_input, None)

    def test_result(self):
        data = fixtures.make_activity_task_data(input=None)
        task = ActivityTask(data)
        self.assertEqual(task.result, None)

        task.set_result('RESULT')
        self.assertEqual(task.result, 'RESULT')

    def test_fail(self):
        data = fixtures.make_activity_task_data()
        task = ActivityTask(data)

        with self.assertRaises(ActivityTaskFailure) as assert_exc:
            task.fail('reason', 'details')

        self.assertEqual(assert_exc.exception.reason, 'reason')
        self.assertEqual(assert_exc.exception.details, 'details')
        self.assertEqual(str(assert_exc.exception), 'reason: details')

    def test_repr(self):
        data = fixtures.make_activity_task_data()
        task = ActivityTask(data)
        repr(task)
