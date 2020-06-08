r4d - rack infrastructure control system
========================================

r4d means 'Remote For Device-under-test' and is an infrastructure for
power-control and console access for multiple Linux Boards that should
be controlled by a test-infrastructure like jenkins.

r4dd (Remote For Device-under-test Daemon) acts as controlling server for test
racks. Each Rack contains a serial device server and a power control switch.
A rack can host several DUTs (device-under-test).
r4d connects to the serial device server and the power switch to perform
actions on user request. A user connects to r4d through a SOAP interface.

All available boards, racks, power-controls and serial servers are represented
in a sqlite database. To show/create or modify the database the 'r4dcfg' tool
can be used. If the tooling is to limited for your needs we recommend to use
the 'SQLite Manager Plugin for Firefox' to manually alter the database.

Have also a look at 'https://github.com/ci-rt/libvirt-debian'. This
project provides a r4d_driver for libvirt. So you can poweron/off the
boards managed in r4d via libvirt. You can even access the serial
console of your boards with a command like 'virsh -c
r4d://localhost:8008 console juno64'

Prerequisite
------------
On Debian systems you can simply run:
"sudo apt install python3-sqlalchemy python3-pysimplesoap python3-snimpy snmp-mibs-downloader"
to satisfy all runtime dependencies.

Note, that the 'snmp-mibs-downloader' package is in the non-free section of
Debian.

Install and run systemd service
-------------------------------
Use 'python3 setup.py install' to build and install r4d.
The so installed systemd service file can be used to control the daemon:

    $ systemctl enable r4dd # start it automatically during system boot
    $ systemctl start r4dd  # start it manually (once)
    $ systemctl stop r4dd   # stop it now

Run from source directory
-------------------------
Simply start "./r4dd"

Configuration
-------------

Config file
~~~~~~~~~~~
The listen interface and port and the used database backend can be altered via
config file that can be passed to r4dd with the -c parameter:

    $ r4dd -c /etc/r4dd.cfg

The format of /etc/r4dd.cfg looks like this:

::

  [r4dd]
  listen=0.0.0.0
  port=8008
  [db]
  echo=0
  uri=sqlite:////usr/share/r4dd/r4d.sqlite
  user=None
  password=None

If no file is given, the above config reflects the defaults.

To add a new power switch, serial console server or a testsystem the
commandline tool "r4dcfg" can be used. This tool should be executed as
the same user who runs the daemon. The daemon creates the database.

Add rack
~~~~~~~~
Please call "r4dcfg --add-rack NAME LOCATION" where NAME is a unique human
readable name of the testrack, e.g. 'ci-linux-rack3'. LOCATION describes the
physical location, e.g. a room number 'SRV07-OU21'.

    $ r4dcfg --add-rack ci-linux-rack3 SRV07-OU21

Add power switch
~~~~~~~~~~~~~~~~
Please call "r4dcfg --add-power RACK MODEL HOST" where RACK is the
human-readable name of the rack the switch is installed in, e.g.
'ci-linux-rack3', MODEL is the power switch model, e.g. 'pc8210' and HOST the
hostname or IP of the new power switch, e.g.
'ci-linux-rack3-power.tec.company.example'

The following models are supported:

- net8x    (Gude Expert Power Control NET 8x)
- pc8210   (Gude Expert Power Control 8210 / 8211)

    $ r4dcfg --add-power ci-linux-rack3 pc8210 ci-linux-rack3-power.tec.company.example

If you get the error "No SNMP response received before timeout"
you need to activate enable SNMP get for public and set for private in the
config / SNMP section of the webinterface of the power control switch.

Add serial console server
~~~~~~~~~~~~~~~~~~~~~~~~~
Please call "r4dcfg --add-serial RACK MODEL HOST" where RACK is the
human-readable name of the rack the serial server is installed in, e.g.
'ci-linux-rack3', MODEL is the serial server model, e.g. 'PS810' and HOST the
hostname or IP of the new serial server, e.g.
'ci-linux-rack3-serial.tec.company.example'

The following model is supported:
- ps810    (Sena Pro Series PS810)

    $ r4dcfg --add-serial ci-linux-rack3 PS810 ci-linux-rack3-serial.tec.company.example

Add device under test
~~~~~~~~~~~~~~~~~~~~~
Please call "r4dcfg --add-board RACK SLOT NAME" where RACK is the
human-readable name of the rack the 'device under test'is installed in, e.g.
'ci-linux-rack3', SLOT is the position inside the rack, e.g. '5' for slot number
5. Slot 5 should be connected with port 5 of the powercontrol switch and port 5
of the serial server. NAME is the name of the new device under test, e.g.
'juno64'

    $ r4dcfg --add-board ci-linux-rack3 5 juno64

Inspect database and testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Use

    $ r4dcfg --show-db

to get an overview of the configured infrastructure.

    $ r4dcfg --list-boards

::

  ID[1]: el9jyJpAN1aZNTGiuQpB6g==
  Name: juno64      Rack: ci-linux-rack3     Port: 5 serial: ci-linux-rack3-serial.tec.company.example:7005

The 'ID[1]' means board is powered, 'ID[0]' board is poweroff and 'ID[-1]'
power state of bard is unknown.

To switch the powerstate off a board, the following commands can be used:

    $ r4dcfg --poweron juno64
    $ r4dcfg --poweroff juno64
    $ r4dcfg --powercycle juno64

This commands are for testing the infrastructure! To control the boards from
e.g. jenkins or other systems in your LAN please use libvirt as described in
the intro!

Move board
~~~~~~~~~~
To move a board to a different rack and/or slot use "r4dcfg --move-board
DST_RACK DST_SLOT NAME" where DST_RACK is the name of the new rack the board
should be placed in, DST_SLOT is the number of the new slot it should be placed
and NAME is the name of the board that should be moved. If DST_RACK is the same
as the current rack the board is placed in the command can be used to move the
board to a different slot in the same rack. E.g. to move the juno64 board into
slot 8 use the following command:

    $ r4dcfg --move-board ci-linux-rack3 8 juno64

Delete board
~~~~~~~~~~~~
To delete a board from the infrastructure you should use "r4dcfg --delete-board
NAME" where NAME is the name of the board to be removed. E.g. to remove the
juno64 board from the infrastructure use:

    $ r4dcfg --delete-board juno64
