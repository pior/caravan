import unittest

import mock
from moto import mock_swf

from caravan.swf import (get_workflow_registration_parameter,
                         register_workflow,
                         get_connection)


class Test(unittest.TestCase):

    def test_get_connection(self):
        swf_connection = get_connection()

        # Boto3 client object are dynamically forged...
        self.assertEqual(swf_connection.__class__.__name__, 'SWF')
        self.assertEqual(swf_connection.__class__.__module__, 'botocore.client')

        self.assertEqual(swf_connection.meta.config.read_timeout, 70)
        self.assertEqual(swf_connection.meta.config.region_name, 'us-east-1')
        self.assertEqual(swf_connection.meta.service_model.service_name, 'swf')

    def test_register_workflow(self):
        class TestWorkflow(object):
            name = 'TestWorkflow'
            version = '1.0'

        connection = get_connection()
        with mock_swf():
            connection.register_domain(
                name='TEST',
                workflowExecutionRetentionPeriodInDays='1')

            result = register_workflow(connection, 'TEST', TestWorkflow)
            self.assertTrue(result)

            # Moto bug : https://github.com/spulec/moto/issues/495
            # result = register_workflow(connection, 'TEST', TestWorkflow)
            # self.assertTrue(result)

            wt = connection.list_workflow_types(domain='TEST',
                                                registrationStatus='REGISTERED')
            self.assertEqual(len(wt['typeInfos']), 1)
            self.assertEqual(wt['typeInfos'][0]['workflowType'],
                             {'name': 'TestWorkflow', 'version': '1.0'})


class UnittestRegisterWorkflow(unittest.TestCase):

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
            defaultTaskList={'name': 'TEST_TL'},
            defaultTaskPriority='TEST_TP',
            defaultTaskStartToCloseTimeout='TEST_TSTCT',
            domain='TESTDOMAIN', name='TESTNAME', version='TESTVERSION')
