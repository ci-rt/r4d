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

import io
import logging
import sys

if sys.version_info >= (3,0):
    from configparser import RawConfigParser
else:
    from ConfigParser import RawConfigParser

log = logging.getLogger (__name__)

class PresetConfigParser (RawConfigParser):
    def __init__ (self, presets):
        super().__init__(self, allow_no_value = True)
        for s in presets.keys():
            self.add_section (s)
            for k,v in presets[s].items():
                self.set (s,k,v)

class R4DdConfig (object):

    def __init__ (self, configname = None):
        log.debug ("r4dd_config.__init__")

        self.__config = PresetConfigParser (self._create_default_config())
        if configname:
            self.load_config (configname)

    def _create_default_config(self):
        """Create a basic working configuration."""

        return {
            "r4dd": {
                "listen": "0.0.0.0",
                "port": 8008
            },
            "db": {
                "echo": "0",
                "uri": "sqlite:///r4d.sqlite",
                "user": None,
                "password": None,
            },
        }

    def load_config (self, name):
        self.__config.read (name)

    def r4dd_conf (self, name):
        return self.__config.get ("r4dd", name)

    def db_conf (self, name):
        return self.__config.get ("db", name)

    def db_conf_bool (self, name):
        return self.__config.getboolean ("db", name)
