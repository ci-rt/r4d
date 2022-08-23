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
from http.server import HTTPServer
from pysimplesoap.server import SoapDispatcher, SOAPHandler

log = logging.getLogger ()


class CustomSOAPHandler(SOAPHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        super().do_GET()

    def do_POST(self):
        super().do_POST()

    def log_message(self, format, *args):
        """Log HTTP requests"""
        log.info(f"New request from {self.address_string()} with arguments '{args}'")

        if "headers" in self.__dict__.keys():
            log.debug(f"Request header: \n{self.headers}")

class R4DSoapService (object):
    def __init__(self):
        log.debug ("R4DSoapService.__init__")
        self.__dispatcher = SoapDispatcher (
            'r4d',
            location = "http://localhost:8008/",
            action = 'http://localhost:8008/',
            namespace = "http://ci-rt.linutronix.de/r4d.wsdl",
            prefix="r4d",
            pretty = True,
            debug = log.level is logging.DEBUG)

    def soap (self, f, name = None, returns = None, args = None, doc = None):
        if not name:
            name = self.__name__
        self.__dispatcher.register_function (name, f,
                                             returns = returns,
                                             args = args, doc = doc)

        log.info(f"Added SOAP Service '{name}'")

    def server_start(self, listen, port):
        httpd = HTTPServer ((listen, port), SOAPHandler)
        httpd.dispatcher = self.__dispatcher

        log.info("Server runs.")
        httpd.serve_forever ()