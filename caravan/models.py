

def normalize_attribute_key(payload):
    key = [k for k in payload.keys() if k.endswith("Attributes")][0]
    payload['attributes'] = payload.pop(key)


class DecisionTask(object):

    def __init__(self, data):
        self.token = data['taskToken']
        self.events = data['events']

        self.workflow_id = data['workflowExecution']['workflowId']
        self.run_id = data['workflowExecution']['runId']
        self.workflow_type = data['workflowType']['name']
        self.workflow_version = data['workflowType']['version']

        self.decisions = []

    def __repr__(self):
        return '<DecisionTask %s v=%s id=%s>' % (self.workflow_type,
                                                 self.workflow_version,
                                                 self.workflow_id)

    @property
    def workflow_input(self):
        execution_event = self.last_event_type("WorkflowExecutionStarted")
        return execution_event['attributes'].get('input')

    def has_event_type(self, event_type):
        return bool(self.last_event_type(event_type))

    def last_event_type(self, event_type):
        events = [e for e in self.events if e['eventType'] == event_type]
        if events:
            event = events[-1]
            normalize_attribute_key(event)
            return event
        else:
            return None

    def add_decision(self, decision_type, **attributes):
        attribute_name = '%s%sDecisionAttributes' % (decision_type[0].lower(),
                                                     decision_type[1:])
        decision_payload = {
            'decisionType': decision_type,
            attribute_name: attributes,
        }
        self.decisions.append(decision_payload)
