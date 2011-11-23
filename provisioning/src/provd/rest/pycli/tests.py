# -*- coding: UTF-8 -*-

"""Various functions to help with testing plugins from the CLI."""

__license__ = """
    Copyright (C) 2011  Avencall

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# importing <module> as _<module> so that import are not autocompleted in the CLI
from pprint import pprint as _pprint
from provd.persist.common import ID_KEY as _ID_KEY

# list of (test config info, test config factory) tuples
_TEST_CONFIGS = []
# test certificate
_TEST_CERT = u"""\
-----BEGIN CERTIFICATE-----
MIICgjCCAiygAwIBAgIJAJwF1KTBOPBuMA0GCSqGSIb3DQEBBQUAMGExCzAJBgNV
BAYTAkNBMQ8wDQYDVQQIEwZRdWViZWMxDzANBgNVBAcTBlF1ZWJlYzEhMB8GA1UE
ChMYSW50ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMQ0wCwYDVQQDEwRUZXN0MB4XDTEx
MDgxMTEyMzEzNFoXDTE0MDgxMDEyMzEzNFowYTELMAkGA1UEBhMCQ0ExDzANBgNV
BAgTBlF1ZWJlYzEPMA0GA1UEBxMGUXVlYmVjMSEwHwYDVQQKExhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQxDTALBgNVBAMTBFRlc3QwXDANBgkqhkiG9w0BAQEFAANL
ADBIAkEAxlYKKK/mUcvR8qR/EvaVu108pLw4wuPCrqzfhLAoprGerXfZP2YhhyYs
GlbrQtbY35OfXgaQlka0GHaJ451JYwIDAQABo4HGMIHDMB0GA1UdDgQWBBTkhtbv
aTHnKF74IAIOiug0940DmzCBkwYDVR0jBIGLMIGIgBTkhtbvaTHnKF74IAIOiug0
940Dm6FlpGMwYTELMAkGA1UEBhMCQ0ExDzANBgNVBAgTBlF1ZWJlYzEPMA0GA1UE
BxMGUXVlYmVjMSEwHwYDVQQKExhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQxDTAL
BgNVBAMTBFRlc3SCCQCcBdSkwTjwbjAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEB
BQUAA0EAbtlcPsrcsuXvxDq60D5AloZhFJoPsvpEcpqz4F9h4JkHWpJLqmXucoAr
hI3UQIC7ov7+c//RAE5gVACKtLNlIQ==
-----END CERTIFICATE-----
"""
# test key (goes with the test certificate by the way)
_TEST_KEY = u"""\
-----BEGIN RSA PRIVATE KEY-----
MIIBOwIBAAJBAMZWCiiv5lHL0fKkfxL2lbtdPKS8OMLjwq6s34SwKKaxnq132T9m
IYcmLBpW60LW2N+Tn14GkJZGtBh2ieOdSWMCAwEAAQI/aiOhTCTWHO/2auOdHYjY
mGxNB9uyhJlelhvtghTDrHBvAXIIja/yBt2L87BNFErqK7ICRK5geHAwD5AHt5Xx
AiEA+fPWMBmqJU1AMuEpagpy7U6GrOdWqlmvAbifD+FW8xkCIQDLIn/z5NrRyEQz
feBrOwSh0y4/JQwf4WBG7lKimHtL2wIhAKi6QUwXBxRHIZ82/43ln88xwxfU0lwM
TmcLCdTeeKOBAiEApMDMimHZYEBPoHu9ovrxHNcNMUW4+bpvvdfZyepmRfUCIQCU
vTY4cAbxNt/187RFuZU/B3NqiQS/OyktZyIoaZ4QTQ==
-----END RSA PRIVATE KEY-----
"""


def _init_module(configs, devices, plugins):
    # MUST be called from another module before the function in this module
    # are made available in the CLI
    global _configs
    global _devices
    global _plugins
    _configs = configs
    _devices = devices
    _plugins = plugins


def remove_all():
    """Remove all the plugins, devices and configs."""
    _plugins.uninstall_all()
    _devices.remove_all()
    _configs.remove_all()


def remove_test_objects():
    """Remove all devices and configs."""
    remove_test_devices()
    remove_test_configs()


def remove_test_configs():
    """Remove all test configs, i.e. all configs which have a key 'X_test'
    set to True.
    
    """ 
    for config in _configs.find({u'X_test': True}, fields=[_ID_KEY]):
        config_id = config[_ID_KEY]
        print 'Removing config %s' % config_id
        _configs.remove(config_id)


def remove_test_devices():
    """Remove all test devices, i.e. all devices which have a key 'X_test'
    set to True.
    
    """
    for device in _devices.find({u'X_test': True}, fields=[_ID_KEY]):
        device_id = device[_ID_KEY]
        print 'Removing device %s' % device_id
        _devices.remove(device_id)


def exec_config_tests(device_id):
    """Execute the config tests using the device with the given device ID."""
    device = _devices[device_id]
    for info, cfg_factory in _TEST_CONFIGS:
        desc = info['description']
        config = cfg_factory()
        while True:
            s = raw_input('Test %s config ? [Y/n/p] ' % desc)
            if not s or s[0].lower() == 'y':
                config[u'X_test'] = True
                cfg_id = _configs.add(config)
                device.set({u'config': cfg_id})
                configured = device.get()[u'configured']
                print '   configured: %s' % configured
                break
            elif s[0].lower() == 'n':
                break
            elif s[0].lower() == 'p':
                _pprint(config)
            else:
                print 'Invalid input %s' % input
            print


def add_test_devices(plugin_id):
    """Add the tests device using plugin with the given ID."""
    _devices.add({
        u'id': u'empty',
        u'X_test': True,
        u'plugin': plugin_id
    })
    _devices.add({
        u'id': u'min',
        u'X_test': True,
        u'mac': u'00:11:22:33:44:00',
        u'plugin': plugin_id
    })


def _test_config(fun):
    description = fun.__name__.lstrip('_').replace('_', ' ')
    _TEST_CONFIGS.append(({'description': description}, fun))
    return fun


@_test_config
def _minimalist():
    return {
        u'parent_ids': [],
        u'raw_config': {}
    }


@_test_config
def _minimalist_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _minimalist_global_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_proxy_ip': u'1.1.1.1',
            u'sip_lines': {
                u'1': {
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _minimalist_mixed_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_proxy_ip': u'1.1.1.0',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _standard_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'registrar_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'auth_username': u'authusername1',
                    u'password': u'password1',
                    u'display_name': u'User 1',
                    u'number': u'number1'
                }
            }
        }
    }


@_test_config
def _different_proxy_and_registrar_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'registrar_ip': u'1.1.1.2',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _backup_proxy_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'backup_proxy_ip': u'1.1.1.2',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _backup_proxy_and_registrar_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'backup_proxy_ip': u'1.1.1.2',
                    u'backup_registrar_ip': u'1.1.1.3',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _non_standard_ports_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'proxy_port': 15060,
                    u'registrar_port': 15061,
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _multiple_lines_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                },
                u'2': {
                    u'proxy_ip': u'1.1.2.1',
                    u'username': u'username2',
                    u'password': u'password2',
                    u'display_name': u'User 2'
                },
                u'3': {
                    u'proxy_ip': u'1.1.3.1',
                    u'username': u'username3',
                    u'password': u'password3',
                    u'display_name': u'User 3'
                }
            }
        }
    }


@_test_config
def _tcp_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_transport': u'tcp',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _tls_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_transport': u'tls',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _tls_with_certificate_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_transport': u'tls',
            u'sip_servers_root_and_intermediate_certificates': _TEST_CERT,
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _global_srtp_preferred_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_srtp_mode': u'preferred',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _global_srtp_required_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_srtp_mode': u'required',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _per_line_srtp_preferred_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1',
                    u'srtp_mode': u'preferred'
                }
            }
        }
    }


@_test_config
def _per_line_srtp_required_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1',
                    u'srtp_mode': u'required'
                }
            }
        }
    }


@_test_config
def _subscribe_mwi_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_subscribe_mwi': True,
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1',
                    u'voicemail': u'*981'
                }
            }
        }
    }


@_test_config
def _global_dtmf_inband_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_dtmf_mode': u'RTP-in-band',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _global_dtmf_rfc2833_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_dtmf_mode': u'RTP-out-of-band',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _global_dtmf_sip_info_sip():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_dtmf_mode': u'SIP-INFO',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _dns_enabled():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'dns_enabled': True,
            u'dns_ip': u'2.2.2.2',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _ntp_enabled():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'ntp_enabled': True,
            u'ntp_ip': u'2.2.2.2',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _vlan_enabled():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'vlan_enabled': True,
            u'vlan_id': u'100',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _vlan_with_priority():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'vlan_enabled': True,
            u'vlan_id': u'100',
            u'vlan_priority': u'5',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _vlan_with_pc_port():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'vlan_enabled': True,
            u'vlan_id': u'100',
            u'vlan_pc_port_id': u'200',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _syslog_enabled():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'syslog_enabled': True,
            u'syslog_ip': u'2.2.2.2',
            u'syslog_port': 515,
            u'syslog_level': u'info',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _admin_username_and_password():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'admin_username': u'ausername',
            u'admin_password': u'apassword',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _user_username_and_password():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'user_username': u'uusername',
            u'user_password': u'upassword',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _timezone_paris():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'timezone': u'Europe/Paris',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _timezone_montreal():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'timezone': u'America/Montreal',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _locale_fr_FR():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'locale': u'fr_FR',
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _config_encryption_enabled():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'config_encryption_enabled': True,
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            }
        }
    }


@_test_config
def _funckey_speeddial():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            },
            u'funckeys': {
                u'1': {
                    u'type': u'speeddial',
                    u'value': u'value1',
                    u'label': u'label1',
                }
            }
        }
    }


@_test_config
def _funckey_blf():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            },
            u'funckeys': {
                u'1': {
                    u'type': u'blf',
                    u'value': u'value1',
                    u'label': u'label1',
                }
            }
        }
    }


@_test_config
def _funckey_park():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.1.1',
                    u'username': u'username1',
                    u'password': u'password1',
                    u'display_name': u'User 1'
                }
            },
            u'funckeys': {
                u'1': {
                    u'type': u'park',
                    u'value': u'value1',
                    u'label': u'label1',
                }
            }
        }
    }


@_test_config
def _full():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'dns_enabled': True,
            u'dns_ip': u'1.1.1.1',
            u'ntp_enabled': True,
            u'ntp_ip': u'1.1.1.2',
            u'vlan_enabled': True,
            u'vlan_id': 1,
            u'vlan_priority': 2,
            u'vlan_pc_port_id': 3,
            u'syslog_enabled': True,
            u'syslog_ip': u'1.1.1.3',
            u'syslog_port': 515,
            u'syslog_level': u'warning',
            u'admin_username': u'adminu',
            u'admin_password': u'adminp',
            u'user_username': u'useru',
            u'user_password': u'userp',
            u'timezone': u'Europe/Paris',
            u'locale': u'fr_FR',
            u'sip_proxy_ip': u'1.1.1.4',
            u'sip_proxy_port': 5061,
            u'sip_backup_proxy_ip': u'1.1.1.5',
            u'sip_backup_proxy_port': 5062,
            u'sip_registrar_ip': u'1.1.1.5',
            u'sip_registrar_port': 5063,
            u'sip_backup_registrar_ip': u'1.1.1.6',
            u'sip_backup_registrar_port': 5063,
            u'sip_outbound_proxy_ip': u'1.1.1.7',
            u'sip_outbound_proxy_port': 5064,
            u'sip_dtmf_mode': u'SIP-INFO',
            u'sip_subscribe_mwi': True,
            u'sip_lines': {
                u'1': {
                    u'proxy_ip': u'1.1.2.1',
                    u'proxy_port': 5160,
                    u'backup_proxy_ip': u'1.1.2.2',
                    u'backup_proxy_port': 5161,
                    u'registrar_ip': u'1.1.2.3',
                    u'registrar_port': 5162,
                    u'backup_registrar_ip': u'1.1.2.4',
                    u'backup_registrar_port': 5163,
                    u'outbound_proxy_ip': u'1.1.2.5',
                    u'outbound_proxy_port': 5164,
                    u'username': u'username1',
                    u'auth_username': u'ausername1',
                    u'password': u'password1',
                    u'display_name': u'User 1',
                    u'number': u'1',
                    u'dtmf_mode': u'SIP-INFO',
                    u'voicemail': u'*981'
                },
                u'2': {
                    u'proxy_ip': u'1.1.3.1',
                    u'proxy_port': 5260,
                    u'backup_proxy_ip': u'1.1.3.2',
                    u'backup_proxy_port': 5261,
                    u'registrar_ip': u'1.1.3.3',
                    u'registrar_port': 5262,
                    u'backup_registrar_ip': u'1.1.3.4',
                    u'backup_registrar_port': 5263,
                    u'outbound_proxy_ip': u'1.1.3.5',
                    u'outbound_proxy_port': 5264,
                    u'username': u'username2',
                    u'auth_username': u'ausername2',
                    u'password': u'password2',
                    u'display_name': u'User 2',
                    u'number': u'2',
                    u'dtmf_mode': u'SIP-INFO',
                    u'voicemail': u'*982'
                }
            },
            u'exten_dnd': u'*dnd',
            u'exten_fwd_unconditional': u'*fwdunc',
            u'exten_fwd_no_answer': u'*fwdnoans',
            u'exten_fwd_busy': u'*fwdbusy',
            u'exten_fwd_disable_all': u'*fwddisable',
            u'exten_park': u'*park',
            u'exten_pickup_group': u'*pckgrp',
            u'exten_voicemail': u'*vmail',
            u'funckeys': {
                u'1': {
                    u'type': u'speeddial',
                    u'value': u'fkv1',
                    u'label': u'fkl1',
                },
                u'2': {
                    u'type': u'blf',
                    u'value': u'fkv2',
                    u'label': u'fkl2',
                },
                u'3': {
                    u'type': u'park',
                    u'value': u'fkv3',
                    u'label': u'fkl3'
                }
            },
            u'X_xivo_phonebook_ip': u'1.1.1.8'
        }
    }


@_test_config
def _minimalist_sccp():
    return {
        u'parent_ids': [],
        u'raw_config': {
            u'sccp_call_managers': {
                u'1': {
                    u'ip': u'1.1.1.1'
                }
            }
        }
    }
