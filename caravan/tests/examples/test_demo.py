import unittest

import mock

from caravan.examples.demo import Demo


class Test(unittest.TestCase):

    def test_signature(self):
        task = mock.Mock()
        workflow = Demo(task)

        self.assertIs(workflow.task, task)
        self.assertEqual(workflow.name, 'Demo')
        self.assertEqual(workflow.version, '0.1')
        self.assertEqual(workflow.default_execution_start_to_close_timeout,
                         '600')
        self.assertEqual(workflow.default_task_start_to_close_timeout, '10')
        self.assertEqual(workflow.default_task_list, 'default')
        self.assertEqual(workflow.default_child_policy, 'TERMINATE')
