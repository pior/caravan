
class Workflow(object):

    """Base implementation of a workflow.

    To implement a workflow, subclass this class and override the class
    attributes and the run method.

    Class attributes to override:

        name (str): Name of the workflow type

        version (str): Version of the workflow type

        description (str|optional): description of the workflow type

        default_task_start_to_close_timeout (optional):
            default maximum duration of decision tasks

        default_execution_start_to_close_timeout (optional):
            default maximum duration for executions

        default_task_list (optional):
            default task list to use for scheduling decision tasks

        default_task_priority (optional):
            default task priority to assign to the workflow type

        default_child_policy (optional):
            default policy to use for the child workflow executions when a
            workflow execution of this type is terminated

        default_lambda_role (optional):
            ARN of the default IAM role to use when a workflow execution of
            this type invokes AWS Lambda functions

        More information on the Boto3 documentation:
        http://boto3.readthedocs.org/en/latest/reference/services/swf.html#SWF.Client.register_workflow_type

    Method to override:

        run()

    Example::

        from caravan import Workflow

        class MyWorkflow(Workflow):

            name = 'MyWorkflow'
            version = '1.0'

            def run(self):
                self.task.add_decision('CompleteWorkflowExecution')
    """

    name = None
    version = None
    description = None


    def __init__(self, task):
        self.task = task

    def __repr__(self):
        return '<Workflow %s(%s)>' % (self.name, self.version)

    def run(self):
        raise NotImplementedError()
