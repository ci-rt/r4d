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
# along with ELBE.  If not, see <http://www.gnu.org/licenses/>.

import logging

from r4d.config import R4DdConfig
from r4d.db import R4DDataBase
from r4d.soap import R4DSoapService
from r4d.rackservice import RackService
from r4d.powerservice import PowerService
from r4d.serialservice import SerialService
from r4d.boardservice import BoardService

log = logging.getLogger (__name__)

class R4Dd (object):
    def __init__ (self, configname):
        log.debug ("r4dd.__init__")
        self.__config = R4DdConfig (configname = configname)
        self.__db = R4DDataBase (self.__config)
        self.__service = R4DSoapService (self.__db)
        self.__power = PowerService (self.__db, self.__service)
        self.__rack = RackService (self.__db, self.__service)
        self.__serial = SerialService (self.__db, self.__service)
        self.__board = BoardService (self.__db, self.__service)

    def main (self):
        print ("Start Server...")

        listen = self.__config.r4dd_conf ("listen")
        port = int (self.__config.r4dd_conf ("port"))

        self.__service.server (listen, port)
