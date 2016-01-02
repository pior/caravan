import unittest

import mock

from caravan.tests import fixtures
from caravan.tests.util import TestUtilMixin
from caravan.commands.activity import Command


@mock.patch('caravan.commands.activity.Worker')
class Test(TestUtilMixin, unittest.TestCase):

    def test_nominal(self, m_worker_cls):
        m_worker = m_worker_cls.return_value
        m_worker.run.side_effect = [None, None, KeyboardInterrupt('KILLTEST')]

        args = [
            '-d', 'DOMAIN', '-m', 'caravan.tests.fixtures', '-t', 'TASKLIST',
            ]

        with self.mock_args(args):
            with self.assertRaises(SystemExit) as exc:
                Command.main()

        self.assertEqual(exc.exception.code, 1)
        self.assertEqual(m_worker.run.call_count, 3)

        args, kwargs = m_worker_cls.call_args
        self.assertEqual(kwargs['domain'], 'DOMAIN')
        self.assertEqual(kwargs['task_list'], 'TASKLIST')
        self.assertEqual(kwargs['entities'],
                         [fixtures.TestActivity1, fixtures.TestActivity2])

        self.assertIsSwfConnection(kwargs['connection'])

    @mock.patch('caravan.commands.activity.register_activity', autospec=True)
    @mock.patch('caravan.commands.activity.get_connection', autospec=True)
    def test_register_activities(self, m_get_conn, m_register, m_worker_cls):
        m_worker = m_worker_cls.return_value
        m_worker.run.side_effect = KeyboardInterrupt('KILLTEST')

        m_conn = m_get_conn.return_value

        args = [
            '-d', 'DOMAIN', '-m', 'caravan.tests.fixtures', '-t', 'TASKLIST',
            '--register-activities',
            ]

        with self.mock_args(args):
            with self.assertRaises(SystemExit):
                Command.main()

        expected = [
            mock.call(connection=m_conn,
                      domain='DOMAIN',
                      activity=fixtures.TestActivity1),
            mock.call(connection=m_conn,
                      domain='DOMAIN',
                      activity=fixtures.TestActivity2),
            ]
        self.assertEqual(m_register.call_args_list, expected)
