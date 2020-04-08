#!/usr/bin/env python3

from glob import glob
from setuptools import setup

from r4d.version import r4d_version

with open("README.rst") as f:
    long_description = f.read()

setup(name='r4d',
      version=r4d_version,
      description='R4D Daemon',
      long_description=long_description,
      author='Benedikt Spranger',
      author_email='b.spranger@linutronix.de',
      url='http://ci-rt.linutronix.de/',
      packages=['r4d', \
                'r4d.power', \
                'r4d.serial' ],
      package_data = {'r4d': ["power/*.txt"]},
      scripts=['r4dd', 'r4dcfg'],
      data_files= [
          ('share/man8/', glob("docs/r4dcfg.8")),
          ('share/man8/', glob("docs/r4dd.8")),
          ('/etc/',                glob("r4dd.cfg")),
          ('/lib/systemd/system',  glob("r4dd.service"))],
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
      ],
)
