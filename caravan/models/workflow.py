
class Workflow(object):

    """Base implementation of a workflow.

    To implement a workflow, subclass this class and override the class
    attributes and the run method.

    Class attributes to override:

        name (str): Name of the workflow type
        version (str): Version of the workflow type
        description (str|optional): description of the workflow type
        defaults (dict|optional):
            Allowed keys:
                TaskStartToCloseTimeout
                ExecutionStartToCloseTimeout
                TaskPriority
                ChildPolicy
                LambdaRole
            See: http://boto3.readthedocs.org/en/latest/reference/services/swf.html#SWF.Client.register_workflow_type

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

    defaults = {}

    def __init__(self, task):
        self.task = task

    def __repr__(self):
        return '<Workflow %s(%s)>' % (self.name, self.version)

    def run(self):
        raise NotImplementedError()
