import os
import socket


IDENTITY_SIZE = 256


def get_default_identity():
    identity = "%s-%s" % (socket.getfqdn(), os.getpid())
    return identity[-IDENTITY_SIZE:]  # keep the most important part
