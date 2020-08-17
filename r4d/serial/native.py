import logging

from r4d.db import SerialControl

log = logging.getLogger (__name__)

def register (parent):
    log.debug ("register " + __name__)
    parent._add_model ('NATIVE', native)

class native (SerialControl):
    __mapper_args__ = {'polymorphic_identity': 'NATIVE'}

    def num_ports (self):
        return 8

    def get_udpport (self, port):
        return (2000 + port)
