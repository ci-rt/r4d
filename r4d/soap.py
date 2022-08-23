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

from base64 import b64encode
from dataclasses import dataclass, field
from http.server import HTTPServer
from http import HTTPStatus
from pysimplesoap.server import SoapDispatcher, SOAPHandler

log = logging.getLogger ()

@dataclass
class BasicAuthentication:
    username: str
    password: str
    key: str = field(init=False, repr=False)

    def __post_init__(self):
        self.key = b64encode(bytes(f"{self.username}:{self.password}", "utf-8")).decode(
            "ascii"
        )

    def __eq__(self, key_to_check):
        """Compare key hash to input key hash"""
        return f"Basic {self.key}" == key_to_check


class CustomSOAPHandler(SOAPHandler):
    def __init__(self, *args, auth=None, **kwargs):
        self.key = None
        if all(auth):
            (user, passwd) = auth
            self.key = BasicAuthentication(username=user, password=passwd)
            log.info("Basic Authentication successful created.")
        else:
            log.info(f"Error in creation Basic Authentication. Authentication input: {auth}")

        super().__init__(*args, **kwargs)

    def _authentication(self):
        """
        Authenticate if headers='Authorization' the same as the dataclass self.key

        If it is the same return True. If it is not the same write the response
        header and the response and return False.
        """

        key_head = self.headers.get("Authorization")

        if self.key == key_head:
            log.info(f"Authentication from {self.address_string()} successful")
            return True

        log.info(f"Authentication from {self.address_string()} not successful")

        self.send_response(HTTPStatus.UNAUTHORIZED)
        self.end_headers()
        return False

    def do_GET(self):
        if self._authentication():
            super().do_GET()

    def do_POST(self):
        if self._authentication():
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