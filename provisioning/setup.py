#!/usr/bin/env python
# -*- coding: UTF-8 -*-


from distutils.core import setup

setup(
    name='provisioning',
    version='0.1',
    description='XIVO provisioning daemon',
    maintainer='Proformatique',
    maintainer_email='technique@proformatique.com',
    url='http://wiki.xivo.fr/',
    license='GPLv3',
    
    packages=['provd',
              'provd.devices',
              'provd.persist',
              'provd.rest',
              'provd.rest.client',
              'provd.rest.pycli',
              'provd.rest.server',
              'provd.servers',
              'provd.servers.tftp',
              'twisted',
              'twisted.plugins'],
    package_dir={'': 'src'},
    package_data={'provd': ['tzinform/tzdatax'],
                  'twisted': ['.noinit'],
                  'twisted.plugins': ['provd_plugins.py', '.noinit']},
    scripts=['dhcpd-update/dhcpd-update',
             'dhcp-xtor/dxtora',
             'dhcp-xtor/dxtorc',
             'scripts/provd_pycli'],
    data_files=[('/etc/pf-xivo/provd', ['resources/etc/provd.conf',
                                        'resources/etc/base_raw_config.json',
                                        'resources/etc/info_extractor.py.conf.default',
                                        'resources/etc/retriever.py.conf.default',
                                        'resources/etc/retriever.py.conf.secure',
                                        'resources/etc/router.py.conf.default',
                                        'resources/etc/updater.py.conf.default',
                                        'resources/etc/updater.py.conf.secure']),
                ('/etc/pf-xivo', ['dhcpd-update/dhcpd-update.conf',
                                  'dhcp-xtor/dxtora.conf']),
                ('/usr/share/doc/dhcp-xtor/', ['dhcp-xtor/dhcpd.conf.example'])],
)
