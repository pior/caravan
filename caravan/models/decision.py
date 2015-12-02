import pprint


def normalize_attribute_key(payload):
    key = [k for k in payload.keys() if k.endswith("Attributes")][0]
    payload['attributes'] = payload.pop(key)
    return payload


class DecisionDone(Exception):
    pass


class WorkflowFailure(Exception):

    def __init__(self, reason, details):
        self.reason = reason
        self.details = details
        super(WorkflowFailure, self).__init__("%s (%s)" % (reason, details))


class DecisionTask(object):

    def __init__(self, data):
        self.events = [normalize_attribute_key(e) for e in data['events']]

        self.token = data['taskToken']
        self.workflow_id = data['workflowExecution']['workflowId']
        self.run_id = data['workflowExecution']['runId']
        self.workflow_type = data['workflowType']['name']
        self.workflow_version = data['workflowType']['version']

        self.decisions = []

    def __repr__(self):
        return '<DecisionTask %s v=%s id=%s runId=%s>' % (
            self.workflow_type,
            self.workflow_version,
            self.workflow_id,
            self.run_id)

    def print_events(self):
        for e in self.events:
            if 'Decision' in e['eventType']:
                continue
            print "==== %3i %s" % (e['eventId'], e['eventType'])
            pprint.pprint(e['attributes'])

    def add_decision(self, decision_type, **attributes):
        attribute_name = '%s%sDecisionAttributes' % (decision_type[0].lower(),
                                                     decision_type[1:])
        decision_payload = {
            'decisionType': decision_type,
            attribute_name: attributes,
        }
        self.decisions.append(decision_payload)

    def fail(self, reason, details='-'):
        raise WorkflowFailure(reason, details)

    def decision_done(self, msg='-'):
        raise DecisionDone('Decision Done: %s' % msg)
