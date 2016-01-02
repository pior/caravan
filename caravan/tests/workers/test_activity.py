import unittest

import mock

from caravan.models.activity_task import ActivityTask
from caravan.workers.activity import Worker
from .. import fixtures


class Test(unittest.TestCase):

    def test_run(self):
        data = fixtures.make_activity_task_data(name='Activity1',
                                                version='1',
                                                input='"IN"')
        m_conn = mock.Mock()
        m_conn.poll_for_activity_task.return_value = data

        activities = [fixtures.TestActivity1, fixtures.TestActivity2]

        worker = Worker(connection=m_conn, domain='DOMAIN',
                        task_list='default', entities=activities)

        worker.run()

        self.assertTrue(m_conn.respond_activity_task_completed.called)
        self.assertFalse(m_conn.respond_activity_task_failed.called)

    def test_poll(self):
        data = fixtures.make_activity_task_data()
        m_conn = mock.Mock()
        m_conn.poll_for_activity_task.return_value = data

        worker = Worker(connection=m_conn, domain='DOMAIN',
                        task_list='default', entities=[])

        task = worker.poll()

        self.assertIsInstance(task, ActivityTask)
        self.assertEqual(task.activity_name, 'NAME')

    def test_poll_timeout(self):
        m_conn = mock.Mock()
        m_conn.poll_for_activity_task.return_value = {}

        worker = Worker(connection=m_conn, domain='DOMAIN',
                        task_list='default', entities=[])

        result = worker.poll()
        self.assertIsNone(result)

    def test_run_task(self):
        m_conn = mock.Mock()

        activities = [fixtures.TestActivity1, fixtures.TestActivity2]

        worker = Worker(connection=m_conn, domain='DOMAIN',
                        task_list='default', entities=activities)

        data = fixtures.make_activity_task_data(name='Activity1',
                                                version='1',
                                                input='"IN"')
        task = ActivityTask(data)
        worker.run_task(task)

        m_conn.respond_activity_task_completed.assert_called_once_with(
            result='"DONE"', taskToken='TASK_TOKEN')
        self.assertFalse(m_conn.respond_activity_task_failed.called)

    def test_run_task_failed(self):
        m_conn = mock.Mock()

        activities = [fixtures.TestActivity1, fixtures.TestActivity2]

        worker = Worker(connection=m_conn, domain='DOMAIN',
                        task_list='default', entities=activities)

        data = fixtures.make_activity_task_data(name='Activity2',
                                                version='2',
                                                input='"IN"')
        task = ActivityTask(data)
        worker.run_task(task)

        m_conn.respond_activity_task_failed.assert_called_once_with(
            details='DETAILS', reason='REASON', taskToken='TASK_TOKEN')
        self.assertFalse(m_conn.respond_activity_task_completed.called)

    def test_run_task_unknown(self):
        m_conn = mock.Mock()

        activities = [fixtures.TestActivity1, fixtures.TestActivity2]

        worker = Worker(connection=m_conn, domain='DOMAIN',
                        task_list='default', entities=activities)

        data = fixtures.make_activity_task_data(name='Activity3')

        task = ActivityTask(data)
        worker.run_task(task)

        self.assertFalse(m_conn.respond_activity_task_completed.called)
        self.assertFalse(m_conn.respond_activity_task_failed.called)
