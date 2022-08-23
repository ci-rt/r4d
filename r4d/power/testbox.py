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
import time

from r4d.db import PowerControl

log = logging.getLogger (__name__)

def register (parent):
    parent.add_model ('testbox', testbox)
    parent.add_model ('testbox-atx', testboxatx)

class testbox (PowerControl):
    __mapper_args__ = {'polymorphic_identity': 'testbox'}

    def num_ports (self):
        return 1

    def poweron (self, port):
        with open("/sys/class/leds/lamobo_r1:opto:powerswitch/brightness", "w") as gpio:
            gpio.write("255")

    def poweroff (self, port):
        with open("/sys/class/leds/lamobo_r1:opto:powerswitch/brightness", "w") as gpio:
            gpio.write("0")

    def powerstatus (self, port):
        with open("/sys/class/leds/lamobo_r1:opto:powerswitch/brightness", "r") as gpio:
            t = gpio.read()
            return int(t)

        return -1

class testboxatx (testbox):
    __mapper_args__ = {'polymorphic_identity': 'testbox-atx'}

    def poweron (self, port):
        super().poweron(port)
        with open("/sys/class/leds/lamobo_r1:opto:relay/brightness", "w") as gpio:
            time.sleep(10)
            gpio.write("255")
            gpio.seek(0)
            time.sleep(0.5)
            gpio.write("0")
