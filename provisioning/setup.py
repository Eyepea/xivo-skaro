#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"

from distutils.core import setup

setup(
    name='provisioning',
    version='0.1',
    description='XIVO provisioning daemon',
    maintainer='Proformatique',
    maintainer_email='technique@proformatique.com',
    url='http://wiki.xivo.fr/',
    license='GPLv3',
    
    packages=['prov',
              'prov.devices',
              'prov.persist',
              'prov.rest',
              'prov.servers',
              'prov.tftp'],
    py_modules=['twisted.plugins.prov_plugin'],
    package_dir={'': 'src',
                 'twisted.plugins': 'resources/'},
    scripts=['dhcp-xtor/dxtora', 'dhcp-xtor/dxtorc'],
    data_files=[('/etc/pf-xivo/prov', ['resources/etc/prov.conf',
                                       'resources/etc/info_extractor.py.conf.default',
                                       'resources/etc/retriever.py.conf.default',
                                       'resources/etc/retriever.py.conf.secure',
                                       'resources/etc/router.py.conf.default',
                                       'resources/etc/updater.py.conf.default',
                                       'resources/etc/updater.py.conf.secure']),
                ('/etc/pf-xivo', ['dhcp-xtor/dxtora.conf']),
                ('/usr/share/doc/dhcp-xtor/', ['dhcp-xtor/dhcpd.conf.example'])],
)
