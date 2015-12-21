import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
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


def get_workflow_registration_parameter(workflow):
    args = {}

    for parameter in REGISTER_WORKFLOW_PARAMETERS:
        attr_name = inflection.underscore(parameter)
        attr_value = getattr(workflow, attr_name, None)

        required = attr_name in REGISTER_WORKFLOW_REQUIRED_PARAMETERS

        if attr_value is None:
            if required:
                raise InvalidWorkflowError('missing attribute %s' % attr_name)

        else:
            is_string = isinstance(attr_value, string_types)
            is_dict = isinstance(attr_value, dict)

            if parameter == 'defaultTaskList' and is_string:
                attr_value = {'name': attr_value}
            if parameter == 'defaultTaskList' and is_dict:
                pass
            elif not is_string:
                raise InvalidWorkflowError('invalid attribute %s' % attr_name)

            args[parameter] = attr_value

    return args


def register_workflow(connection, domain, workflow):
    """Register a workflow type.

    Return False if this workflow already registered (and True otherwise).
    """
    args = get_workflow_registration_parameter(workflow)

    try:
        connection.register_workflow_type(domain=domain, **args)
    except ClientError as err:
        if err.response['Error']['Code'] == 'TypeAlreadyExistsFault':
            return False  # Ignore this error
        raise

    return True


def get_connection():
    # Must increase the http timeout since SWF has a timeout of 60 sec
    config = Config(connect_timeout=50, read_timeout=70)
    connection = boto3.client("swf", config=config)
    return connection
