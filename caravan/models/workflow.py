
class Workflow(object):
    """Base implementation of a workflow."""

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
