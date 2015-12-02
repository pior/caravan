import pprint
from collections import Counter

import arrow

from caravan import WorkflowFailure, Workflow
from .util import swf_encode_data, swf_decode_data


# def normalize_attribute_key(payload):
#     key = [k for k in payload.keys() if k.endswith("Attributes")][0]
#     payload['attributes'] = payload.pop(key)
#     return payload


def as_list_dict(iterable):
    """Build a dict of list from a list of tuple like (key, value)."""
    dict_of_list = {}
    for key, value in iterable:
        dict_of_list.setdefault(key, []).append(value)
    return dict_of_list


class ScheduleTaskFailed(WorkflowFailure):
    pass


class StartTaskFailed(WorkflowFailure):
    pass


class TaskFailed(WorkflowFailure):
    pass


class TaskTimedOut(WorkflowFailure):
    pass


class BaseTracker(object):

    def __init__(self):
        self.history = []
        self.by_type = {}
        self.last_by_type = {}
        self.counter = Counter()

    def append(self, event):
        self.history.append(event)
        self.by_type.setdefault(event['eventType'], []).append(event)
        self.last_by_type[event['eventType']] = event
        self.counter.update([event['eventType']])

    @property
    def failure(self):
        failure_event = self.last_by_type.get(self.FAILURE_EVENT)
        if failure_event:
            return failure_event['attributes']

    @property
    def started(self):
        return self.STARTED_EVENT in self.last_by_type

    @property
    def complete(self):
        return self.COMPLETE_EVENT in self.last_by_type


class ActivityTaskTracker(BaseTracker):

    EVENTS = [
        'ActivityTaskScheduled',
        'ScheduleActivityTaskFailed',
        'ActivityTaskStarted',
        'ActivityTaskCompleted',
        'ActivityTaskFailed',
        'ActivityTaskTimedOut',
        'ActivityTaskCanceled',
        'ActivityTaskCancelRequested',
        'RequestCancelActivityTaskFailed',
        ]


class LambdaTracker(BaseTracker):

    STARTED_EVENT = 'LambdaFunctionStarted'

    EVENTS = [
        'LambdaFunctionScheduled',
        'LambdaFunctionStarted',
        'LambdaFunctionCompleted',
        'LambdaFunctionFailed',
        'LambdaFunctionTimedOut',
        'ScheduleLambdaFunctionFailed',
        'StartLambdaFunctionFailed',
        ]


class TimerTracker(BaseTracker):

    START_EVENT = 'TimerStarted'
    COMPLETE_EVENT = 'TimerFired'
    FAILURE_EVENT = 'StartTimerFailed'

    EVENTS = [
        'TimerStarted',
        'StartTimerFailed',
        'TimerFired',
        'TimerCanceled',
        'CancelTimerFailed',
        ]


class History(object):

    def __init__(self, events):
        # self.events = [normalize_attribute_key(e) for e in events]
        self.events = events
        self.events_by_id = {e['eventId']: e for e in self.events}

        self.decisions = []
        self.timers = {}
        self.lambda_functions = {}
        self.activity_tasks = {}

        event_map = {
            TimerTracker: self.timers,
            LambdaTracker: self.lambda_functions,
            ActivityTaskTracker: self.activity_tasks
            }

        for event in self.events:
            event_type = event['eventType']

            if event_type == 'WorkflowExecutionStarted':
                self.execution_started = event
                continue

            if 'Decision' in event_type:
                self.decisions.append(event)
                continue

            for tracker, attr in event_map.items():
                if event_type in tracker.EVENTS:
                    call_id = self._get_call_id_from_event(event)
                    attr.setdefault(call_id, tracker()).append(event)

    def print_debug(self):
        for e in self.events:
            if 'Decision' in e['eventType']:
                continue
            print "==== %3i %s" % (e['eventId'], e['eventType'])
            pprint.pprint(e['attributes'])

    def _dereference_event(self, event):
        schedule_event_id = event['attributes'].get('scheduledEventId')
        if schedule_event_id:
            return self.events_by_id[schedule_event_id]
        else:
            return event

    def _get_call_id_from_event(self, event):
        event = self._dereference_event(event)
        attributes = event['attributes']
        if 'activityId' in attributes:
            return attributes['activityId']
        if 'id' in attributes:
            return attributes['id']
        elif 'timerId' in attributes:
            return attributes['timerId']
        else:
            raise RuntimeError("No id found in this event: %s" % event)


class TaskResult(object):

    """Proxy for a task result."""

    def __init__(self, result=None, exception=None, schedule_cb=None,
                 wait_cb=None):
        self._result = result
        self._exception = exception
        self._scheduled = False
        self._schedule_cb = schedule_cb
        self._wait_cb = wait_cb

    @property
    def result(self):
        """Block until the task result is available and return it.
        Raise an exception if task failed."""
        if self._exception:
            raise self._exception
        if self._result is None:
            self.wait()
        else:
            return self._result

    @property
    def done(self):
        """Whether this task is done."""
        return self._result is not None

    @property
    def failed(self):
        """Whether this task failed."""
        return self._exception is not None

    @property
    def scheduled(self):
        """Whether this task was already scheduled in the past."""
        return self._schedule_cb is None

    def wait(self):
        """Block until task is finished. Raise an exception if task failed."""
        if self._exception:
            raise self._exception
        self.schedule()
        if self._wait_cb:
            self._wait_cb()

    def schedule(self):
        """Force scheduling of this task (if needed)."""
        if self._schedule_cb and not self._scheduled:
            self._schedule_cb()
            self._scheduled = True


class Context(object):

    def __init__(self, task):
        self.task = task
        self.history = History(task.events)

        self.swf_now = arrow.get(self.history.events[-1]['eventTimestamp'])

        execution_event = self.history.execution_started
        try:
            input = execution_event['attributes'].get('input')
            self.workflow_input = swf_decode_data(input)
        except Exception as exc:
            self.fail(reason='workflow_input_invalid_json',
                      details=str(exc))
            self.decision_done()

    def fail(self, reason, details):
        self.task.add_decision('FailWorkflowExecution',
                               reason=reason,
                               details=details)

    def complete(self, result=None):
        result = swf_encode_data(result)
        self.task.add_decision('CompleteWorkflowExecution', result=result)

    def decision_done(self):
        self.task.decision_done()

    def execute_activity(self, name, version, task_id, input):
        history = self.history.activity_tasks.get(task_id)

        def wait():
            self.decision_done()

        if not history:
            activity_type = {'name': name, 'version': version}

            def schedule():
                self.task.add_decision(
                    'ScheduleActivityTask',
                    activityId=task_id,
                    activityType=activity_type,
                    input=swf_encode_data(input)
                    )

            # This task must be scheduled
            return TaskResult(schedule_cb=schedule, wait_cb=wait)

        if 'ActivityTaskCompleted' in history.last_by_type:
            event = history.last_by_type['ActivityTaskCompleted']
            result = event['attributes']['result']
            result = swf_decode_data(result)
            return TaskResult(result=result)

        if 'ScheduleActivityTaskFailed' in history.last_by_type:
            event = history.last_by_type['ScheduleActivityTaskFailed']
            exception = ScheduleTaskFailed(
                reason='Activity schedule failed',
                details=event['attributes']['cause'])
            return TaskResult(exception=exception)

        if 'ActivityTaskFailed' in history.last_by_type:
            event = history.last_by_type['ActivityTaskFailed']
            exception = TaskFailed(
                reason=event['attributes']['reason'],
                details=event['attributes']['details'])
            return TaskResult(exception=exception)

        if 'ActivityTaskTimedOut' in history.last_by_type:
            event = history.last_by_type['ActivityTaskTimedOut']
            exception = TaskTimedOut(
                reason='Activity timed out',
                details=event['attributes']['details'])
            return TaskResult(exception=exception)

        # TODO: activity cancellation support

        # This task is already scheduled and didn't fail: just wait for the
        # result
        return TaskResult(wait_cb=wait)

    def execute_lambda(self, name, task_id, input):
        history = self.history.lambda_functions.get(task_id)

        # TODO: Just pass self.decision_done in wait_cb
        # Or refactor TaskResult more deeply to include the Context
        def wait():
            self.decision_done()

        if not history:
            def schedule():
                self.task.add_decision(
                    'ScheduleLambdaFunction',
                    id=task_id,
                    name=name,
                    input=swf_encode_data(input)
                    )

            # This task must be scheduled
            return TaskResult(schedule_cb=schedule, wait_cb=wait)

        if 'LambdaFunctionCompleted' in history.last_by_type:
            event = history.last_by_type['LambdaFunctionCompleted']
            result = event['attributes']['result']
            result = swf_decode_data(result)
            return TaskResult(result=result)

        if 'ScheduleLambdaFunctionFailed' in history.last_by_type:
            event = history.last_by_type['ScheduleLambdaFunctionFailed']
            exception = ScheduleTaskFailed(
                reason='Lambda schedule failed',
                details=event['attributes']['cause'])
            return TaskResult(exception=exception)

        if 'StartLambdaFunctionFailed' in history.last_by_type:
            event = history.last_by_type['StartLambdaFunctionFailed']
            exception = StartTaskFailed(
                reason='Lambda start failed',
                details=event['attributes']['cause'])
            return TaskResult(exception=exception)

        if 'LambdaFunctionFailed' in history.last_by_type:
            event = history.last_by_type['LambdaFunctionFailed']
            exception = TaskFailed(
                reason=event['attributes']['reason'],
                details=event['attributes']['details'])
            return TaskResult(exception=exception)

        if 'LambdaFunctionTimedOut' in history.last_by_type:
            event = history.last_by_type['LambdaFunctionTimedOut']
            exception = TaskTimedOut(
                reason='Lambda task timed out',
                details=event['attributes']['timeoutType'])
            return TaskResult(exception=exception)

        # This task is already scheduled and didn't fail: just wait for the
        # result
        return TaskResult(wait_cb=wait)

    def wait_for_date(self, timer_id, date_to_wait):
        now = self.swf_now  # Use SWF time as reference
        seconds_to_activation = (date_to_wait - now).total_seconds()

        # Wait if activation time is really in the future
        # Timers fire _right_ before the correct scheduled time
        must_wait = seconds_to_activation > 1

        timer = self.history.timers.get(timer_id)

        if must_wait:
            timer = self.history.timers.get(timer_id)

            if not timer:
                start_to_fire_timeout = str(int(seconds_to_activation))
                self.task.add_decision(
                    'StartTimer',
                    timerId=timer_id,
                    startToFireTimeout=start_to_fire_timeout)
                self.decision_done()

            if timer.complete:
                # TODO: Should we really assume the timer was right ?
                return

            if timer.failure:
                self.fail(reason='Timer failed to start',
                          details=timer.failure['cause'])
                self.decision_done()


class BaseWorkflow(Workflow):

    def __init__(self, task):
        self.context = Context(task)

    def run(self):
        raise NotImplementedError()

    def report_status(self, task_id_suffix, delivery=None, total_tasks=None,
                      newly_completed_tasks=None, newly_failed_tasks=None):
        campaign = self.context.workflow_input['campaign']
        config = self.context.workflow_input['config']

        task_id = 'feedback-%s' % task_id_suffix

        task_input = {
            'campaign': campaign,
            'config': config,
            'feedback': {
                'delivery': delivery,
                'total_tasks': total_tasks,
                'newly_completed_tasks': newly_completed_tasks,
                'newly_failed_tasks': newly_failed_tasks,
            }
        }
        task = self.context.execute_lambda(name='px-campaign-feedback',
                                           task_id=task_id,
                                           input=task_input)
        task.wait()
