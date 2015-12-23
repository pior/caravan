from __future__ import print_function

from caravan import Workflow


class Demo(Workflow):

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

            else:
                print("Unknown signal '%s'" % signal_name)
                self.task.decision_done(msg='JustIgnoringThisUnknownSignal')

        else:
            self.task.fail('unknown_event_type')
