#!/usr/bin/python
# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"

from distutils.core import setup

setup(name='fetchfw2',
      version='1.0',
      description='Library and tool for downloading and installing remote files.',
      author='Proformatique',
      author_email='technique@proformatique.com',
      url='http://xivo.fr/',
      package_dir={'': 'src'},
      packages=['fetchfw2'],
      data_files=[('/etc/pf-xivo', ['resources/etc/fetchfw2.conf']),
                  ('/usr/sbin', ['scripts/xivo_fetchfw2']),
                  ('/var/lib/pf-xivo/fetchfw2/installable',
                        ['resources/data/files.db',
                         'resources/data/install.db',
                         'resources/data/packages.db'])]
      )
