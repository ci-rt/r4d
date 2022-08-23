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
import r4d.serial

from r4d.db import SerialControl, SerialPort, Board, Rack
from pysimplesoap.server import SoapFault
from sqlalchemy.exc import IntegrityError
from r4d.tools import register_modules

log = logging.getLogger (__name__)

class SerialService (object):
    def __init__ (self, db, service):
        log.debug ('SerialService.__init__')

        # register callbacks
        if service:
            service.soap (self.get_serial,
                          'get-serial',
                          returns = {'host': str, 'port': int},
                          args = {'system': str})

        self.__db = db
        self.__models = {}
        register_modules (self, r4d.serial)

    def add_model (self, model, f):
        log.debug(f"_add_serial_model: '{model}'")
        self.__models.update ({model: f})

    def get_models (self):
        models = list (self.__models)
        return models

    def add_serial (self, model, host, _rack):
        """Add Serialcontrol"""
        try:
            M = self.__models [model]
        except Exception:
            log.error ("unknown model " + model)
            return -1


        session = self.__db.get_session ()
        session.begin (subtransactions=True)

        rack = session.query(Rack).filter(Rack.name == _rack).one ()
        if rack.serialcontrol:
            log.error (" a serialcontrol is already assigned to this rack")
            return -1

        serial = M (URI = host, rack_id = rack.id)
        session.add (serial)

        try:
            session.commit ()
        except IntegrityError as e:
            log.error (e)
            session.rollback ()
            session.close ()
            return -1

        for i in range (1, serial.num_ports () + 1):
            port = SerialPort (port = i, udpport = serial.get_udpport(i), serialcontrol_id = serial.id);
            session.add (port)

        try:
            session.commit ()
        except IntegrityError as e:
            log.error (e)
            session.rollback ()
            session.close ()
            return -1

        session.close ()
        return 0

    def get_serial (self, system):
        """Get Serialcontrol"""
        serport = {'host': 'none', 'port': -1}
        session = self.__db.get_session ()
        try:
            board = session.query (Board).filter_by (name = system).one ()
            serial = session.query (SerialControl).filter_by (rack_id = board.slot.rack_id).one ()
            port = session.query (SerialPort).filter_by (serialcontrol_id = serial.id, port = board.slot.position).one ()
            serport = {'host': serial.URI, 'port': port.udpport}
        except Exception as e:
            raise SoapFault (faultcode = "SerialGetSerialFailed",
                             faultstring = "get serial of {} failed".format (system),
                             detail = e)
        finally:
            session.close ()

        return serport

    def list_serial (self):
        """list Serialcontrols"""
        l = []
        session = self.__db.get_session ()
        try:
            for host in session.query (SerialControl):
               l.append ({'id': host.id,
                          'host': host.URI,
                          'model': host.model,
                          'ports': host.ports})
        except Exception as e:
            log.error ("serial control query failed: {}".format (e))
            return {'result': -1}
        return {'result': 0, 'list': l}
