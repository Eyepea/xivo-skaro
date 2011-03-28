# -*- coding: UTF-8 -*-

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2010-2011  Proformatique <technique@proformatique.com>

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

import re
import socket


def to_ip(ip_string):
    """Takes a human readable IP address unicode string (i.e. '127.0.0.1')
    and return a 4-bytes string representation of it.
    
    >>> to_ip(u'255.255.255.255')
    '\\xff\\xff\\xff\\xff'
    >>> to_ip(u'192.168.32.106')
    '\\xc0\\xa8 j'
    
    """
    try:
        return socket.inet_aton(ip_string.encode('ascii'))
    except socket.error:
        raise ValueError("'%s' is not a valid dotted quad IPv4 address")


def from_ip(packed_ip):
    """Takes a 4-bytes string representation of an IP and return the human
    readable representation as a unicode string.
    
    >>> # Double escape seems to be needed for the doctest module...
    >>> from_ip('\\xff\\xff\\xff\\xff')
    u'255.255.255.255'
    >>> from_ip('\\xc0\\xa8 j')
    u'192.168.32.106'
    
    """
    try:
        return socket.inet_ntoa(packed_ip).decode('ascii')
    except socket.error:
        raise ValueError("'%s' is not a valid packed IPv4 address")


def norm_ip(ip_string):
    """Return a normalized representation of an IPv4 address string, which
    is the dotted quad notation.
    
    Raise a ValueError if the IPv4 address is invalid. 
    
    """
    return from_ip(to_ip(ip_string))


_MAC_ADDR = re.compile(ur'^[\da-fA-F]{1,2}([:-]?)(?:[\da-fA-F]{1,2}\1){4}[\da-fA-F]{1,2}$')

def to_mac(mac_string):
    """Takes a human readable MAC address unicode string (i.e.
    u'00:1a:2b:33:44:55') and return a 6-bytes string representation of it.
    
    Here's some accepted value:
    - 00:1a:2b:3c:4d:5e
    - 00-1a-2b-3c-4d-5e
    - 00:1A:2B:3C:4D:5E
    - 00:1A:2B:3C:4d:5e
    - 001a2b3c4d5e
    - 001A2B3C4D5E
    - 00:A:2B:C:d:5e
    
    >>> to_mac(u'ff:ff:ff:ff:ff:ff')
    '\\xff\\xff\\xff\\xff\\xff\\xff'
    
    """
    m = _MAC_ADDR.match(mac_string)
    if not m:
        raise ValueError('invalid MAC string')
    sep = m.group(1)
    if not sep:
        # no separator - length must be equal to 12 in this case
        if len(mac_string) != 12:
            raise ValueError('invalid MAC string')
        return ''.join(chr(int(mac_string[i:i+2], 16)) for i in xrange(0, 12, 2))
    else:
        tokens = mac_string.split(sep)
        return ''.join(chr(int(token, 16)) for token in tokens)


def from_mac(packed_mac, separator=u':', uppercase=False):
    """Takes a 6-bytes string representation of a MAC address and return the
    human readable representation.
    
    >>> from_mac('\\xff\\xff\\xff\\xff\\xff\\xff', u':', False)
    u'ff:ff:ff:ff:ff:ff'
    
    """
    if len(packed_mac) != 6:
        raise ValueError('invalid packed MAC')
    if uppercase:
        fmt = u'%02X'
    else:
        fmt = u'%02x'
    return separator.join(fmt % ord(e) for e in packed_mac)


def norm_mac(mac_string):
    """Return a lowercase, separated by colon, representation of a MAC
    address string.
    
    Raise a ValueError if the IPv4 address is invalid.
    
    >>> norm_mac(u'0011223344aa')
    u'00:11:22:33:44:aa'
    >>> norm_mac(u'0011223344AA')
    u'00:11:22:33:44:aa'
    >>> norm_mac(u'00-11-22-33-44-AA')
    u'00:11:22:33:44:aa'
    >>> norm_mac(u'00:11:22:33:44:aa')
    u'00:11:22:33:44:aa'
     
    """
    return from_mac(to_mac(mac_string))


def format_mac(mac_string, separator=u':', uppercase=False):
    """Return a freely formatted representation of a MAC address string."""
    return from_mac(to_mac(mac_string), separator, uppercase)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
