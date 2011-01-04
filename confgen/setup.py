#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "$Revision$ $Date$"

from distutils.core import setup

setup(
	name='pf-xivo-confgen',
	version='0.1',
	description='XIVO Configurations Generator',
	author='Guillaume Bour',
	author_email='gbour@proformatique.com',
	maintainer='Proformatique',
	maintainer_email='technique@proformatique.com',
	url='http://wiki.xivo.fr/',
	license='GPLv3',
	 
	packages=['confgen'],
	package_dir={'confgen': 'xivo_confgen'},
	scripts=['bin/confgen', 'bin/confgend'],
	data_files=[('/etc/pf-xivo', ['etc/confgen.conf', 'etc/confgend.conf'])],
)

