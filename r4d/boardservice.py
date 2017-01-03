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

from binascii import b2a_base64
from r4d.db import PowerPort, Slot, Rack, Board
from platform import node
from pysimplesoap.server import SoapFault
from sqlalchemy.exc import IntegrityError
from uuid import NAMESPACE_URL, UUID, uuid5

log = logging.getLogger (__name__)

class BoardService (object):
    def __init__ (self, db, service):
        log.debug ('BoardService.__init__')

        # register callbacks
        if service:
            service.soap (self.soap_list_boards,
                          'list-systems',
                          args = {'name': str},
                          returns = {'list': [{'location': str,
                                               'name': str,
                                               'port': int,
                                               'rack': str,
                                               'uuid': str}]})
        self.__db = db

    def add_board (self, name, rackname, slotnr):
        session = self.__db.get_session ()
        try:
            uri = 'r4d://' + node () + '/' + name

            rack = session.query (Rack).filter_by (name=rackname).one ()
            slot = session.query (Slot).filter_by (rack_id=rack.id, position=slotnr).one ()
            uuid = uuid5 (NAMESPACE_URL, str (uri))
            board = Board (name=name, slot_id=slot.id, URI=uri, uuid = uuid.hex)
            session.add (board)
            session.commit ()

        except IntegrityError as e:
            session.rollback ()
            log.error (e)

        session.close ()
        return 0

    def move_board (self, name, rackname, slotnr):
        session = self.__db.get_session ()
        try:
            board = session.query (Board).filter_by (name=name).one ()
            rack = session.query (Rack).filter_by (name=rackname).one ()
            dst_slot = session.query (Slot).filter_by (rack_id=rack.id, position=slotnr).one ()
            board.slot = dst_slot
            session.add (board)
            session.commit ()
        except IntegrityError as e:
            session.rollback ()
            log.error (e)
        session.close ()
        return 0

    def delete_board (self, name):
        session = self.__db.get_session ()
        try:
            board = session.query (Board).filter_by (name=name).one ()
            session.delete (board)
            session.commit ()
        except IntegrityError as e:
            session.rollback ()
            log.error (e)
        session.close ()
        return 0


    def list_boards (self, name = None):
        l = []
        session = self.__db.get_session ()
        try:
            q = session.query (Board)
            if name:
                q = q.filter_by (name = name)
            for board in q:
                uuid = UUID (hex = board.uuid)
                log.info (str(uuid))
                l.append ({'location': board.slot.rack.location,
                           'name': board.name,
                           'port': board.slot.position,
                           'rack': board.slot.rack.name,
                           'uuid': b2a_base64 (uuid.bytes_le)})
        except Exception as e:
            log.error ("board query failed: {}".format (e))
            return {'result': -1}
        finally:
            session.close ()
        return {'result': 0, 'list': l}

    def soap_list_boards (self, name):
        if name:
            l = self.list_boards (name = name)
        else:
            l = self.list_boards ()

        if l['result'] == -1:
            raise SoapFault (faultcode = "ListSystemsFailed",
                             faultstring = "could not list boards")

        return {'list': l['list']}
