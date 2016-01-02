import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
from six import string_types
import inflection


class InvalidWorkflowError(Exception):
    pass


def get_swf_parameters(workflow, parameters):
    param_dict = {}

    for parameter in parameters:
        attr_name = inflection.underscore(parameter)
        attr_value = getattr(workflow, attr_name, None)

        required = attr_name in ['name', 'version']

        if attr_value is None:
            if required:
                raise InvalidWorkflowError('missing attribute %s' % attr_name)

        else:
            is_string = isinstance(attr_value, string_types)
            is_dict = isinstance(attr_value, dict)
            is_int = isinstance(attr_value, int)

            if parameter == 'defaultTaskList' and is_string:
                attr_value = {'name': attr_value}
            if parameter == 'defaultTaskList' and is_dict:
                pass
            if parameter.endswith('Timeout') and is_int:
                attr_value = str(attr_value)
            elif not is_string:
                raise InvalidWorkflowError('invalid attribute %s' % attr_name)

            param_dict[parameter] = attr_value

    return param_dict


WORKFLOW_PARAMETERS = [
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


def register_workflow(connection, domain, workflow):
    """Register a workflow type.

    Return False if this workflow already registered (and True otherwise).
    """
    args = get_swf_parameters(workflow, WORKFLOW_PARAMETERS)

    try:
        connection.register_workflow_type(domain=domain, **args)
    except ClientError as err:
        if err.response['Error']['Code'] == 'TypeAlreadyExistsFault':
            return False  # Ignore this error
        raise

    return True


ACTIVITY_PARAMETERS = [
    'name',
    'version',
    'description',
    'defaultTaskStartToCloseTimeout',
    'defaultTaskHeartbeatTimeout',
    'defaultTaskList',
    'defaultTaskPriority',
    'defaultTaskScheduleToStartTimeout',
    'defaultTaskScheduleToCloseTimeout',
    ]


def register_activity(connection, domain, activity):
    """Register an activity type.

    Return False if this activity already registered (and True otherwise).
    """
    args = get_swf_parameters(activity, ACTIVITY_PARAMETERS)

    try:
        connection.register_activity_type(domain=domain, **args)
    except ClientError as err:
        if err.response['Error']['Code'] == 'TypeAlreadyExistsFault':
            return False  # Ignore this error
        raise

    return True


def get_connection():
    """Create and return a Boto3 connection for SWF (with read_timeout=70)."""
    config = Config(connect_timeout=50, read_timeout=70)
    connection = boto3.client("swf", config=config)
    return connection
