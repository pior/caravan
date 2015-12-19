from botocore.exceptions import ClientError
from six import string_types
import inflection


class InvalidWorkflowError(Exception):
    pass


REGISTER_WORKFLOW_PARAMETERS = [
    'name',
    'version',
    'description',
    'defaultTaskStartToCloseTimeout',
    'defaultExecutionStartToCloseTimeout',
    'defaultTaskList',
    'defaultTaskPriority',
    'defaultChildPolicy',
    'defaultLambdaRole',
    ]

REGISTER_WORKFLOW_REQUIRED_PARAMETERS = [
    'name',
    'version',
    ]


def register_workflow(connection, domain, workflow):
    """Register a workflow type.

    Return False if this workflow already registered (and True otherwise).
    """
    args = {}

    for parameter in REGISTER_WORKFLOW_PARAMETERS:
        attr_name = inflection.underscore(parameter)
        attr_value = getattr(workflow, attr_name, None)

        required = attr_name in REGISTER_WORKFLOW_REQUIRED_PARAMETERS

        if attr_value is None:
            if required:
                raise InvalidWorkflowError('missing attribute %s' % attr_name)

        else:
            if attr_name == 'defaultTaskList':
                attr_value = {'name': attr_value}

            elif not isinstance(attr_value, string_types):
                raise InvalidWorkflowError('invalid attribute %s' % attr_name)

            args[parameter] = attr_value

    try:
        connection.register_workflow_type(domain=domain, **args)
    except ClientError as err:
        if err.response['Error']['Code'] == 'TypeAlreadyExistsFault':
            return False  # Ignore this error
        raise

    return True
