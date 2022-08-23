# r4dd - rack infrastructure control daemon
#
# Copyright (C) 2019  Linutronix GmbH
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
import os

from r4d.db import PowerControl
from snimpy.manager import Manager
from snimpy.manager import load

log = logging.getLogger (__name__)

mibpath = os.path.dirname (__file__)
load (os.path.join (mibpath, "GUDEADS-EPC8210-MIB.txt"))

def register (parent):
    parent.add_model ('pc8210v4', pc8210)

class pc8210 (PowerControl):
    __mapper_args__ = {'polymorphic_identity': 'pc8210v4'}

    def num_ports (self):
        m = Manager (self.URI, "public", 2)
        return m.epc8210portNumber

    def poweron (self, port):
        m = Manager (self.URI, "private", 2)
        m.epc8210PortState [port] = 1

    def poweroff (self, port):
        m = Manager (self.URI, "private", 2)
        m.epc8210PortState [port] = 0

    def powerstatus (self, port):
        m = Manager (self.URI, "public", 2)
        return m.epc8210PortState [port]
