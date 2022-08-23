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

from importlib import import_module
from pkgutil import iter_modules

log = logging.getLogger (__name__)

def register_modules (parent, module):
    for _, file_name, _ in iter_modules (module.__path__):
        module_path = f"{module.__name__}.{file_name}"
        try:
            log.info (f"Trying to register module {module_path}...")
            module = import_module (module_path)
            module.register (parent)
            log.info (module_path + "OK.")
        except Exception as e:
            log.error (module_path + "failed.")
            log.error (e)
