#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "$Revision: 10243 $ $Date: 2011-02-23 11:22:26 +0100 (Wed, 23 Feb 2011) $"

from distutils.core import setup

setup(
	name='xivo-ha',
	version='0.1',
	description='XIVO High Availability configurator',
	author='Nicolas HICHER',
	author_email='nhicher@proformatique.com',
	maintainer='Proformatique',
	maintainer_email='technique@proformatique.com',
	url='http://wiki.xivo.fr/',
	license='GPLv3',
	 
	packages=['xivo_ha'],
	package_dir={'xivo_ha': 'xivo_ha'},
	scripts=['bin/pf-xivo-ha'],
	data_files=[
                ('/etc/pf-xivo', ['etc/pf-xivo-ha.conf']),
                ('/usr/share/pf-xivo-ha/templates', [
                                                     'templates/corosync/default_corosync',
                                                     'templates/corosync/corosync.conf',
                                                    ])
               ]
)