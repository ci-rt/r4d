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
import re

from r4d.db import SerialControl

log = logging.getLogger (__name__)

def register (parent):
    parent.add_model ('testbox', testbox)

class testbox (SerialControl):
    __mapper_args__ = {'polymorphic_identity': 'testbox'}

    def num_ports (self):
        return 1

    def get_udpport (self, port):
        try:
            f = open('/etc/ser2net.conf')
        except IOError:
            log.warn("ser2net configuration not found. Use default port 7001.")
            return 7001
        else:
            with f:
                datafile = f.readlines()
                for line in datafile:
                    line = re.sub(r"#.*", "", line)
                    line = re.sub(r"BANNER.*", "", line)
                    if 'testbox' in line:
                        return re.search(r"(^[^:]*)", line).group()

        log.warn("Missing testbox entries in ser2net config. Use default port 7001.")
        return 7001
