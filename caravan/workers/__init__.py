import os
import socket
import logging

log = logging.getLogger(__name__)

IDENTITY_SIZE = 256


def get_default_identity():
    identity = "%s-%s" % (socket.getfqdn(), os.getpid())
    return identity[-IDENTITY_SIZE:]  # keep the most important part


class BaseWorker(object):

    def __init__(self, connection, domain, task_list, entities):
        self.conn = connection
        self.domain = domain
        self.task_list = task_list
        self.entities = dict(((e.name, e.version), e) for e in entities)
        self.identity = get_default_identity()

    def run(self):
        log.info('Waiting for a task...')
        task = self.poll()
        if task:
            log.info('Got a %r', task)
            self.run_task(task)
