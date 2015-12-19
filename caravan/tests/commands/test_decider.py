import unittest

import mock

import caravan
from caravan.tests import fixtures
from caravan.tests.util import mock_args
from caravan.commands.decider import Command
from caravan.commands.decider import ClassesLoaderFromModule
from caravan.commands.decider import register_workflow


@mock.patch('caravan.commands.decider.Worker')
class Test(unittest.TestCase):

    def test_nominal(self, m_worker_cls):
        m_worker = m_worker_cls.return_value
        m_worker.run.side_effect = [None, None, KeyboardInterrupt('KILLTEST')]

        args = [
            '-d', 'DOMAIN', '-m', 'caravan.tests.fixtures', '-t', 'TASKLIST',
            ]

        with mock_args(args):
            with self.assertRaises(SystemExit) as exc:
                Command.main()

        self.assertEqual(exc.exception.code, 1)
        self.assertEqual(m_worker.run.call_count, 3)

        args, kwargs = m_worker_cls.call_args
        self.assertEqual(kwargs['domain'], 'DOMAIN')
        self.assertEqual(kwargs['task_list'], 'TASKLIST')
        self.assertEqual(kwargs['workflows'],
                         [fixtures.TestWorkflow1, fixtures.TestWorkflow2])

        # Boto3 client object are dynamically forged...
        swf_connection = kwargs['connection']
        self.assertEqual(swf_connection.__class__.__name__, 'SWF')
        self.assertEqual(swf_connection.__class__.__module__, 'botocore.client')

    @mock.patch('caravan.commands.decider.register_workflow', autospec=True)
    @mock.patch('caravan.commands.decider.get_swf_connection', autospec=True)
    def test_register_workflows(self, m_get_conn, m_register, m_worker_cls):
        m_worker = m_worker_cls.return_value
        m_worker.run.side_effect = KeyboardInterrupt('KILLTEST')

        m_conn = m_get_conn.return_value

        args = [
            '-d', 'DOMAIN', '-m', 'caravan.tests.fixtures', '-t', 'TASKLIST',
            '--register-workflows',
            ]

        with mock_args(args):
            with self.assertRaises(SystemExit):
                Command.main()

        expected = [
            mock.call(connection=m_conn,
                      domain='DOMAIN',
                      workflow=fixtures.TestWorkflow1),
            mock.call(connection=m_conn,
                      domain='DOMAIN',
                      workflow=fixtures.TestWorkflow2),
            ]
        self.assertEqual(m_register.call_args_list, expected)


class TestClassLoader(unittest.TestCase):

    def test_nominal(self):
        loader = ClassesLoaderFromModule(caravan.Workflow)
        result = loader('caravan.tests.fixtures')
        self.assertEqual(
            result, [fixtures.TestWorkflow1, fixtures.TestWorkflow2])


class TestRegisterWorkflow(unittest.TestCase):

    def test_nominal(self):
        connection = mock.Mock()

        class Workflow(object):
            name = 'TESTNAME'
            version = 'TESTVERSION'

        register_workflow(connection, 'TESTDOMAIN', Workflow)

        connection.register_workflow_type.assert_called_once_with(
            domain='TESTDOMAIN', name='TESTNAME', version='TESTVERSION')

    def test_description(self):
        connection = mock.Mock()

        class Workflow(object):
            name = 'TESTNAME'
            version = 'TESTVERSION'
            description = 'TESTDESC'

        register_workflow(connection, 'TESTDOMAIN', Workflow)

        connection.register_workflow_type.assert_called_once_with(
            description='TESTDESC', domain='TESTDOMAIN',
            name='TESTNAME', version='TESTVERSION')

    def test_defaults(self):
        connection = mock.Mock()

        class Workflow(object):
            name = 'TESTNAME'
            version = 'TESTVERSION'

            default_task_start_to_close_timeout = 'TEST_TSTCT'
            default_execution_start_to_close_timeout = 'TEST_ESTCT'
            default_task_list = 'TEST_TL'
            default_task_priority = 'TEST_TP'
            default_child_policy = 'TEST_CP'
            default_lambda_role = 'TEST_LR'

        register_workflow(connection, 'TESTDOMAIN', Workflow)

        connection.register_workflow_type.assert_called_once_with(
            defaultChildPolicy='TEST_CP',
            defaultExecutionStartToCloseTimeout='TEST_ESTCT',
            defaultLambdaRole='TEST_LR',
            defaultTaskList='TEST_TL',
            defaultTaskPriority='TEST_TP',
            defaultTaskStartToCloseTimeout='TEST_TSTCT',
            domain='TESTDOMAIN', name='TESTNAME', version='TESTVERSION')
