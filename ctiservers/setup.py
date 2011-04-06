#!/usr/bin/env python

__version__ = "$Revision: 8982 $ $Date: 2010-08-23 13:18:20 +0200 (Mon, 23 Aug 2010) $"

from distutils.core import setup

setup(name='xivo_daemon',
      version='1.0',
      description='XiVO CTI Server Daemon',
      author='Proformatique',
      author_email='technique@proformatique.com',
      url='http://xivo.fr/',
      packages=['xivo_ctiservers',
		'xivo_ctiservers.lists'],
      data_files=[
		  ('/usr/sbin', ['xivo_daemon']),
		 ],
     )
