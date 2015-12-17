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
        self.assertEqual(workflow.defaults['ExecutionStartToCloseTimeout'],
                         '600')
        self.assertEqual(workflow.defaults['TaskStartToCloseTimeout'],
                         '10')
        self.assertEqual(workflow.defaults['TaskList'],
                         'default')
        self.assertEqual(workflow.defaults['ChildPolicy'],
                         'TERMINATE')
