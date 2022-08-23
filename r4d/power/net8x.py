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
import sys

from r4d.db import PowerControl

if sys.version_info >= (3,0):
    from html.parser import HTMLParser
    from urllib.request import urlopen
else:
    from HTMLParser import HTMLParser
    from urllib2 import urlopen

log = logging.getLogger (__name__)

def register (parent):
    parent.add_model ('net8x', net8x)

class net8xHTMLParser(HTMLParser):
    old = ""
    status = {}

    def handle_data (self, data):
        d = {'ON': 1, 'OFF': 0}
        if data.find ("Power Port") >= 0:
            self.status [int (data.strip ()[-1:])] = d [self.old.strip ()]

        self.old = data

class net8x (PowerControl):
    __mapper_args__ = {'polymorphic_identity': 'net8x'}
    parser = net8xHTMLParser ()

    def __change (self, port, state):
        req = "http://{}/switch.html?cmd=1&p={}&s={}".format (self.URI,
                                                              port,
                                                              state)
        log.info (req)
        f = urlopen (req)
        log.info (f.read ())
        f.close ()

    def num_ports (self):
        return 8

    def poweron (self, port):
        self.__change (port, 1)

    def poweroff (self, port):
        self.__change (port, 0)

    def powerstatus (self, port):
        self.parser.status = {}

        f = urlopen ("http://" + self.URI)
        self.parser.feed (f.read ().decode ('utf-8'))
        f.close()

        try:
            return self.parser.status [port]
        except KeyError as e:
            return -1
