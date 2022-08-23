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
import r4d.power

from r4d.db import PowerControl, PowerPort, Board, Rack
from pysimplesoap.server import SoapFault
from sqlalchemy.exc import IntegrityError
from r4d.tools import register_modules

log = logging.getLogger (__name__)

class PowerService (object):
    def __init__ (self, db, service):
        log.debug ('PowerService.__init__')

        # register callbacks
        if service:
            service.soap (self.change,
                          'power-change',
                          args = {'system': str, 'state': bool},
                          returns = {'state': bool})

            service.soap (self.status,
                          'power-status',
                          args = {'system': str},
                          returns = {'state': bool})

        self.__db = db
        self.__models = {}
        register_modules (self, r4d.power)

    def add_model (self, model, f):
        log.debug(f"_add_power_model: '{model}'")
        self.__models.update ({model: f})

    def get_models (self):
        models = list (self.__models)
        return models

    def add_power (self, model, host, _rack):
        """Add Powercontrol"""
        try:
            M = self.__models [model]
        except KeyError:
            log.error ("unknown model " + model)
            return -1

        session = self.__db.get_session ()
        session.begin (subtransactions=True)

        rack  = session.query(Rack).filter(Rack.name == _rack).one ()
        if rack.powercontrol:
            log.error (" a powercontrol is already assigned to this rack")
            return -1

        power = M (URI = host, rack_id = rack.id)
        session.add (power)

        try:
            session.commit ()
        except IntegrityError as e:
            log.error (e)
            session.rollback ()
            session.close ()
            return -1

        for i in range (1, power.num_ports () + 1):
            port = PowerPort (port = i, powercontrol_id = power.id);
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

    def change (self, system, state):
        """Change Power Status"""
        session = self.__db.get_session ()
        try:
            board = session.query (Board).filter_by (name = system).one ()
            if board.slot:
                pos = board.slot.position
                if not board.slot or  not board.slot.rack or not board.slot.rack.powercontrol:
                        return {'state': False}
                pc_id = board.slot.rack.powercontrol.id
                powerport = session.query (PowerPort).filter_by (port = pos, powercontrol_id = pc_id).one ()
                if powerport:
                    if (int (state)):
                        powerport.poweron ()
                    else:
                        powerport.poweroff ()
                else:
                    return {'state': False}

        except Exception as e:
            log.error ("power: change status of {} failed: {}".format (system, e))
            raise SoapFault (faultcode = "PowerChangeFailed",
                             faultstring = "change status of {} failed".format (system),
                             detail = e)
        finally:
            session.close ()

        return {'state': True}

    def status (self, system):
        """Get Testsystem Power Status"""
        session = self.__db.get_session ()
        try:
            board = session.query (Board).filter_by (name = system).one ()
            if board.slot:
                pos = board.slot.position
                pc_id = board.slot.rack.powercontrol.id
                powerport = session.query (PowerPort).filter_by (port = pos, powercontrol_id = pc_id).one ()
                state = powerport.powerstatus ()
        except Exception as e:
            log.error ("power: get status of {} failed: {}".format (system, e))
            raise SoapFault (faultcode = "PowerStatusFailed",
                             faultstring = "get status of {} failed".format (system),
                             detail = e)
        finally:
            session.close ()
        return bool (state)

    def list_power (self):
        """list Powercontrols"""
        l = []
        session = self.__db.get_session ()

        try:
            for host in session.query (PowerControl):
                l.append ({'id': host.id,
                           'host': host.URI,
                           'model': host.model,
                           'ports': host.ports})
        except Exception as e:
            log.error ("power control query failed: {}".format (e))
            session.close ()
            return {'result': -1}

        session.close ()
        return {'result': 0, 'list': l}
