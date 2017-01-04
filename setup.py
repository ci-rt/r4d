#!/usr/bin/env python

from glob import glob
from distutils.core import setup

from r4d.version import r4d_version

setup(name='r4d',
      version=r4d_version,
      description='R4D Daemon',
      author='Benedikt Spranger',
      author_email='b.spranger@linutronix.de',
      url='http://ci-rt.linutronix.de/',
      packages=['r4d', \
                'r4d.power', \
                'r4d.serial' ],
      package_data = {'r4d': ["power/*.txt"]},
      scripts=['r4dd', 'r4dcfg'],
      data_files= [
          ('/usr/share/doc/r4dd/', glob("README.adoc")),
          ('/usr/share/r4dd/',     glob("r4d.sqlite")),
          ('/etc/',                glob("r4dd.cfg")),
          ('/lib/systemd/system',  glob("r4dd.service"))],
)
