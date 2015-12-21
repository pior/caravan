from moto import mock_swf

from caravan.swf import register_workflow, get_connection


def valid_workflow_registration(workflow):
    connection = get_connection()
    with mock_swf():
        connection.register_domain(name='TEST',
                                   workflowExecutionRetentionPeriodInDays='1')
        register_workflow(connection, 'TEST', workflow)

