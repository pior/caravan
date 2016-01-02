from __future__ import print_function
import time

from caravan import Workflow, Activity


class DemoWorkflow(Workflow):

    """Demo workflow using the bare caravan API."""

    name = 'Demo'
    version = '0.1'
    default_execution_start_to_close_timeout = 600
    default_task_start_to_close_timeout = 10
    default_task_list = 'default'
    default_child_policy = 'TERMINATE'

    def run(self):
        # For development, you can print the history events
        print("")
        self.task.print_events()

        # Minimalist History evaluation, just consider the last event
        non_decision_events = [e for e in self.task.events
                               if not e['eventType'].startswith('Decision')]
        last_event = non_decision_events[-1]

        if last_event['eventType'] == 'WorkflowExecutionStarted':
            # This is the start of this execution !
            # First, let's wait for a signal using a timer
            self.task.add_decision('StartTimer',
                                   startToFireTimeout='300',
                                   timerId='SignalTimeout')
            self.task.decision_done(msg='JustStartedATimer')

        elif last_event['eventType'] == 'TimerFired':
            # The timer fired! Timeout!
            # We fail the whole workflow execution (while providing a reason)
            self.task.fail('patience_lost')

        elif last_event['eventType'] == 'WorkflowExecutionSignaled':
            # Hey! We received a Signal!

            signal_name = last_event['attributes']['signalName'].upper()
            # signal_input = last_event['input']

            if signal_name == 'ABORT':
                # Fail the workflow execution right now
                self.task.fail('aborted')

            elif signal_name == 'PRINT':
                # Let's print the Signal input (payload)
                signal_input = last_event['attributes'].get('input')
                print("\nThe signal input is: '%s'" % signal_input)

            elif signal_name == 'STOP':
                # Mark this workflow execution as complete
                workflow_result = '{"success": true}'
                self.task.add_decision('CompleteWorkflowExecution',
                                       result=workflow_result)

            elif signal_name == 'ACTIVITY':
                # Schedule a demo activity
                activity_type = {
                    'name': DemoActivity.name,
                    'version': DemoActivity.version,
                    }
                activity_id = str(time.time())
                self.task.add_decision('ScheduleActivityTask',
                                       activityType=activity_type,
                                       activityId=activity_id,
                                       input='"DemoInput"')

            else:
                print("Unknown signal '%s'" % signal_name)
                self.task.decision_done(msg='JustIgnoringThisUnknownSignal')

        else:
            print('Unknown last event type')


class DemoActivity(Activity):

    name = 'DemoActivity'
    version = '0.1.2'

    default_task_list = 'default'

    default_task_start_to_close_timeout = 60
    default_task_schedule_to_start_timeout = 10
    default_task_schedule_to_close_timeout = 70
    default_task_heartbeat_timeout = 'NONE'

    def run(self, input):
        print('Received input: %s' % input)
        self.do_stuff()
        return {'input': input, 'output': 'YO'}

    def do_stuff(self):
        print('Doing stuff (waiting 3 secs)')
        time.sleep(2)
