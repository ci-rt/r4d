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

from r4d.db import Rack, Slot

from pysimplesoap.server import SoapFault

log = logging.getLogger (__name__)

class RackService (object):
    def __init__ (self, db, service):
        log.debug ('RackService.__init__')

        # register callbacks
        if service:
            service.soap (self.list_racks,
                          'list-racks',
                          returns = {'list': [{'name': str}]},
                          args = {})

        self.__db = db

    def add_rack (self, name, location, desc="", num_slots=8):
        session = self.__db.get_session ()
        try:
            rack = Rack (name=name, location=location, description=desc)
            for i in range(num_slots):
                slot = Slot (position=i+1)
                rack.slots.append (slot)
            session.add (rack)
            session.commit ()
        except Exception as e:
            log.error ("add new rack failed: {}".format (e))
            raise SoapFault (faultcode = "AddRackFailed",
                             faultstring = "could not add a new rack",
                             detail = e)
        finally:
            session.close ()

    def list_racks (self):
        """list Testracks"""
        l = []
        session = self.__db.get_session ()
        try:
            for rack in session.query (Rack):
                l.append ({'id': rack.id,
                           'name': rack.name,
                           'location': rack.location})

        except Exception as e:
            log.error ("testrack query failed: {}".format (e))
            raise SoapFault (faultcode = "ListSystemsFailed",
                             faultstring = "could not list testracks",
                             detail = e)
        finally:
            session.close ()

        log.info (l)
        return l
