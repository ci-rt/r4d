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

from binascii import hexlify, unhexlify
from hashlib import pbkdf2_hmac
from os import urandom
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger (__name__)
Base = declarative_base ()

class PowerControl (Base):
    __tablename__ = 'powercontrol'

    id = Column (Integer, primary_key = True, autoincrement=True)

    URI      = Column (String, unique = True)
    rack_id  = Column (Integer, ForeignKey('rack.id'))
    rack     = relationship ("Rack", back_populates="powercontrol")
    ports    = relationship ("PowerPort", backref="powercontrol")
    model    = Column (String)
    __mapper_args__ = {'polymorphic_on': model}

    def __repr__ (self):
        return ("    Power[%s] %s" % (str(self.model), self.URI))

class PowerPort (Base):
    __tablename__ = 'powerport'

    id = Column (Integer, primary_key = True, autoincrement=True)
    powercontrol_id = Column (Integer, ForeignKey('powercontrol.id'))
    port = Column (Integer)

    def num_ports (self):
        return self.powercontrol.num_ports (self.port)
    def poweron (self):
        return self.powercontrol.poweron (self.port)
    def poweroff (self):
        return self.powercontrol.poweroff (self.port)
    def powerstatus (self):
        return self.powercontrol.powerstatus (self.port)

class SerialControl (Base):
    __tablename__ = 'serialcontrol'

    id = Column (Integer, primary_key = True, autoincrement=True)

    URI      = Column (String, unique = True)
    rack_id  = Column (Integer, ForeignKey('rack.id'))
    rack     = relationship ("Rack", back_populates="serialcontrol")
    ports    = relationship ('SerialPort', backref='serialcontrol')
    model    = Column (String)
    __mapper_args__ = {'polymorphic_on': model}

    def __repr__ (self):
        return ("    Serial[%s] %s" % (self.model, self.URI))

class SerialPort (Base):
    __tablename__ = 'serialport'

    id = Column (Integer, primary_key = True, autoincrement=True)

    serialcontrol_id = Column (Integer, ForeignKey ('serialcontrol.id'))
    port             = Column (Integer)
    udpport          = Column (Integer)

    def num_ports (self):
        self.control.num_ports (self.udpport)

class Slot (Base):
    __tablename__ = 'slot'

    id = Column (Integer, primary_key = True, autoincrement=True)

    position  = Column (Integer)
    rack_id   = Column (Integer, ForeignKey('rack.id'))
    board     = relationship ("Board", uselist=False, back_populates="slot")

    def __repr__ (self):
        return ("    ==SLOT[%d]== id<%d>" % (self.position, self.id))

class Rack (Base):
    __tablename__ = 'rack'

    id = Column (Integer, primary_key = True, autoincrement=True)

    name          = Column (String, unique = True)
    location      = Column (String)
    description   = Column (String)
    slots         = relationship ("Slot", backref = "rack")
    serialcontrol = relationship ("SerialControl", uselist=False, back_populates="rack")
    powercontrol  = relationship ("PowerControl", uselist=False, back_populates="rack")

    def __repr__ (self):
        desc = ("==Rack[%s]== id<%d>\n" % (self.name, self.id))
        if self.serialcontrol:
            desc += str(self.serialcontrol) + "\n"
        if self.powercontrol:
            desc += str(self.powercontrol)
        return desc

class Board (Base):
    __tablename__ = 'board'

    id = Column (Integer, primary_key = True, autoincrement=True)

    name    = Column (String, unique = True)
    URI     = Column (String)
    uuid    = Column (String (32), unique = True)
    slot_id = Column (Integer, ForeignKey ('slot.id'))
    slot    = relationship ("Slot", back_populates="board")

    def __repr__ (self):
        return ("        Board[%s] id<%d>" % (self.name, self.id))

class R4DDataBase (object):
    def __init__ (self, config):
        log.debug ("r4dd_db.__init__")

        self.__engine = create_engine (config.db_conf ('uri'),
                                       echo = config.db_conf_bool ('echo'))
        Base.metadata.create_all (self.__engine)
        self.__Session = sessionmaker (bind = self.__engine)

    def print_config (self):
        session = self.__Session ()
        racks = session.query(Rack)
        for r in racks:
            print (r)
            for s in r.slots:
                print (s)
                if (s.board):
                    print (s.board)
        session.close ()

    def get_session (self):
        return self.__Session ()

    def get_engine (self):
        return self.__engine
