#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""Small client program that send DHCP information to the transfer agent via
a Unix [datagram] socket.

The client takes the DHCP information via it's command line. For example, if
the lease 192.168.1.1 has just been committed by the DHCP server to the DHCP
client with the MAC address 00:11:22:33:44:55, if the script had been call
from a shell, it could have look like:

  dxtorc.py 'commit' '192.168.1.1' '00:11:22:33:44:55'

It can also take additional info about the DHCP request, for example, the
option vendor-class-identifier with value of 'foobar':

  dxtorc.py 'commit' '192.168.1.1' '00:11:22:33:44:55' '060666f6f6261720a'

Note: 60 is the DHCP code for the option vendor class identifier [RFC2132], and
      everything after the first 3 digit is the option value represented in
      hexadecimal.

Empty arguments after the MAC address are ignored.

The first argument can also be one of 'release' or 'expiry'. In this case,
only the IP address needs to be passed to the client:

  xtorc.py 'release' '192.168.1.1'

"""

import socket
import sys
import StringIO

UNIX_SERVER_ADDR = '/var/run/dxtora.ctl'


def msg_exit(err_msg):
    print >>sys.stderr, err_msg
    sys.exit(1)


def parse_args(args):
    """Return a dhcp_info object from the command line arguments..."""
    dhcp_info = {}
    try:
        dhcp_info['op'] = args[0]
        dhcp_info['ip'] = args[1]
        if dhcp_info['op'] == 'commit':
            dhcp_info['mac'] = args[2]
            dhcp_info['dhcp_opts'] = filter(None, args[3:])
        elif dhcp_info['op'] in ('expiry', 'release'):
            pass
        else:
            msg_exit('error: invalid operation')
    except IndexError:
        msg_exit('error: not enough arguments')
    else:
        return dhcp_info


def build_dgram(dhcp_info):
    """Return a datagram from an dhcp_info object...""" 
    s = StringIO.StringIO()
    def append(v):
        s.write(v + '\n')
    append(dhcp_info['op'])
    append(dhcp_info['ip'])
    if dhcp_info['op'] == 'commit':
        append(dhcp_info['mac'])
        for dhcp_opt in dhcp_info['dhcp_opts']:
            append(dhcp_opt)
    return s.getvalue()


def send_dgram(dgram):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    # It's important to set the socket to non-blocking since we do not
    # want to slow down the calling process (i.e. the DHCP server).
    s.setblocking(0)
    try:
        s.sendto(dgram, UNIX_SERVER_ADDR)
    except socket.error:
        msg_exit('error: could not send data to remote socket')
    finally:
        s.close()


if __name__ == '__main__':
    send_dgram(build_dgram(parse_args(sys.argv[1:])))
