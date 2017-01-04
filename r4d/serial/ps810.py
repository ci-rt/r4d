# r4dd - rack infrastructure control daemon
#
# Copyright (C) 2016  Linutronix GmbH
# Author: Benedikt Spranger <b.spranger@linutronix.de>
#
# This file is part of r4d.
#
# r4d is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# r4d is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with r4d.  If not, see <http://www.gnu.org/licenses/>.

import logging

from r4d.db import SerialControl

log = logging.getLogger (__name__)

def register (parent):
    log.debug ("register " + __name__)
    parent._add_model ('PS810', ps810)

class ps810 (SerialControl):
    __mapper_args__ = {'polymorphic_identity': 'PS810'}

    def num_ports (self):
        return 8

    def get_udpport (self, port):
        return (7000 + port)
