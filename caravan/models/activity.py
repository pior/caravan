from caravan.codecs import gzipjson


class Activity(object):

    """Base implementation of an activity.

    To implement a activity, subclass this class and override the attributes
    and the run method.

    Class attributes to override:

        name (str): Name of the workflow type

        version (str): Version of the workflow type

        description (str|optional): description of the workflow type

        default_task_start_to_close_timeout (optional):
            maximum duration of decision tasks

        default_task_heartbeat_timeout (optional):
            maximum time before which a worker processing a task of this type
            must report progress by calling RecordActivityTaskHeartbeat

        default_task_list (optional):
            default task list to use for scheduling decision tasks

        default_task_priority (optional):
            task priority to assign to the activity type. (default to 0)
            Valid values: -2147483648 to 2147483647. Higher numbers indicate
            higher priority.

        default_task_schedule_to_start_timeout (optional):
            maximum duration that a task of this activity type can wait before
            being assigned to a worker. The value "NONE" can be used to specify
            unlimited duration.

        default_task_schedule_to_close_timeout (optional):
            maximum duration for a task of this activity type. The value "NONE"
            can be used to specify unlimited duration.

        More information on the Boto3 documentation:
        http://boto3.readthedocs.org/en/latest/reference/services/swf.html#SWF.Client.register_activity_type

    Method to override:

        run()

    Example::

        from caravan import Activity

        class DoStuff(Activity):

            name = 'DoStuff'
            version = '1.0'

            def run(self, input):
                result = do_stuff(input)
                return result
    """

    name = None
    version = None
    description = None

    codec = gzipjson

    def __init__(self, task):
        self.task = task

    def __repr__(self):
        return '<Activity %s(%s)>' % (self.name, self.version)

    def _run(self):
        task_input = self.codec.loads(self.task.task_input)
        task_result = self.run(task_input)
        self.task.set_result(self.codec.dumps(task_result))

    def run(self):
        raise NotImplementedError()
