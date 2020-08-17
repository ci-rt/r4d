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

# SWITCH_ADDRESS="147.11.86.11"
# BASE_SWITCH_OID="1.3.6.1.4.1.318.1.1.4.4.2.1.3"
# power_on_device()
# {
#    echo "Powering on device $1"
#    snmpset -v1 -cprivate $SWITCH_ADDRESS $BASE_SWITCH_OID.$1 i 1 >> /dev/null
# }

# power_off_device()
# {
#    echo "Powering off device $1"
#    snmpset -v1 -cprivate $SWITCH_ADDRESS $BASE_SWITCH_OID.$1 i 2 >> /dev/null
# }

# reboot_device()
# {
#    echo "Rebooting device $1"
#    snmpset -v1 -cprivate $SWITCH_ADDRESS $BASE_SWITCH_OID.$1 i 3 >> /dev/null
# }


import logging
import os

from r4d.db import PowerControl
from snimpy.manager import Manager
from snimpy.manager import load

log = logging.getLogger (__name__)

mibpath = os.path.dirname (__file__)
load (os.path.join (mibpath, "powernet404.mib"))
def register (parent):
    log.debug ("register " + __name__)
    parent._add_model ('apc', apc)

class apc (PowerControl):
    __mapper_args__ = {'polymorphic_identity': 'apc'}

    def num_ports (self):
        m = Manager (self.URI, "public", 2)
        return m.rPDUOutletDevNumTotalOutlets

    def poweron (self, port):
        numeric = int(port);
        m = Manager (self.URI, "private", 2)
        m.rPDUOutletControlOutletCommand[port] = 'immediateOn'

    def poweroff (self, port):
        m = Manager (self.URI, "private", 2)
        m.rPDUOutletControlOutletCommand[port] = 'immediateOff'

    def powerstatus (self, port):
        m = Manager (self.URI, "public", 2)
        if m.rPDUOutletStatusOutletState[port] == 2:
            return 1
        if m.rPDUOutletStatusOutletState[port] == 1:
            return 0
        return -1;
