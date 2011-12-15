# -*- coding: UTF-8 -*-

"""Low-level functions to manipulate packets and datagrams.

A packet is a dictionary object. A dgram (datagram) is a string object.

"""

__license__ = """
    Copyright (C) 2010-2011  Avencall

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

OP_RRQ = '\x00\x01'
OP_WRQ = '\x00\x02'
OP_DATA = '\x00\x03'
OP_ACK = '\x00\x04'
OP_ERR = '\x00\x05'
OP_OACK = '\x00\x06'

ERR_UNDEF = '\x00\x00'     # Not defined, see error message (if any)
ERR_FNF = '\x00\x01'     # File not found
ERR_ACCESS = '\x00\x02'     # Access violation
ERR_ALLOC = '\x00\x03'     # Disk full or allocation exceeded
ERR_ILL = '\x00\x04'     # Illegal TFTP operation
ERR_UNKNWN_TID = '\x00\x05'     # Unknown transfer ID
ERR_FEXIST = '\x00\x06'     # File already exists
ERR_NO_USER = '\x00\x07'     # No such user


class PacketError(Exception):
    """Raise when a problem with parsing/building a datagram arise."""
    pass


def _parse_option_blksize(string):
    try:
        blksize = int(string)
    except ValueError:
        raise PacketError('invalid blksize value - not a number')
    else:
        if blksize < 8 or blksize > 65464:
            raise PacketError('invalid blksize value - out of range')
        return blksize


_PARSE_OPT_MAP = {
    'blksize': _parse_option_blksize,
}

def _parse_request(dgram):
    """dgram is the original datagram with the first 2 bytes removed.
    
    TFTP option extension is supported.
    
    """
    # XXX RFC2347 (TFTP Option Extension) says request should not be longer
    #     than 512 byte, but we omit this check since I don't think we care
    # Note: 'file\x00mode\x00'.split('\x00') == ['file', 'mode', '']
    tokens = dgram.split('\x00')
    if len(tokens) < 3:
        raise PacketError('too small')
    elif dgram[-1] != '\x00':
        assert tokens[-1]
        raise PacketError('last dgram byte not null')
    elif len(tokens) % 2 == 0:
        raise PacketError('invalid number of field')
    else:
        options = {}
        for i in xrange(2, len(tokens) - 1, 2):
            opt = tokens[i].lower()
            val = tokens[i + 1].lower()
            if opt in options:
                # An option may only be specified once
                raise PacketError('same option specified more than once')
            opt_fct = _PARSE_OPT_MAP.get(opt, lambda x: x)
            options[opt] = opt_fct(val)
        return {'filename': tokens[0], 'mode': tokens[1].lower(), 'options': options}


def _parse_data(dgram):
    if len(dgram) < 2:
        raise PacketError('too small')
    else:
        return {'blkno': dgram[:2], 'data': dgram[2:]}


def _parse_ack(dgram):
    if len(dgram) != 2:
        raise PacketError('incorrect size')
    else:
        return {'blkno': dgram}


def _parse_err(dgram):
    if len(dgram) < 3:
        raise PacketError('too small')
    elif dgram[-1] != '\x00':
        raise PacketError('last datagram byte not null')
    else:
        return {'errcode': dgram[:2], 'errmsg': dgram[2:-1]}


_PARSE_MAP = {
    OP_RRQ: _parse_request,
    OP_WRQ: _parse_request,
    OP_DATA: _parse_data,
    OP_ACK: _parse_ack,
    OP_ERR: _parse_err,
}

def parse_dgram(dgram):
    """Return a packet object (a dictionary) from a datagram (a string).
    
    Raise a PacketError if the datagram is not parsable (i.e. invalid). Else,
    return a dictionary with the following keys:
      opcode -- the opcode of the packet as a 2-byte string
    
    The others keys in the dictionary depends on the type of the packet.
    
    Read/write request:
      filename -- the filename
      mode -- the mode
      options -- a possibly empty dictionary of option/value

    Data packet:
      blkno -- the block number as a 2-byte string
      data -- the data
    
    Ack packet:
      blkno -- the block number as a 2-byte string

    Error packet:
      errcode -- the error code as a 2-byte string
      errmsg -- the error message
    
    Option acknowledgement datagrams are currently not supported. Also,
    case-insensitive field (mode field of request packet and option name)
    are returned in lowercase.
    
    """
    opcode = dgram[:2]
    try:
        fct = _PARSE_MAP[opcode]
    except KeyError:
        raise PacketError('invalid opcode')
    else:
        res = fct(dgram[2:])
        res['opcode'] = opcode
        return res


def _build_data(packet):
    if len(packet['blkno']) != 2:
        raise PacketError('invalid blkno length')
    else:
        return packet['blkno'] + packet['data']


def _build_error(packet):
    if len(packet['errcode']) != 2:
        raise PacketError('invalid errcode length')
    elif '\x00' in packet['errmsg']:
        raise PacketError('null byte in errmsg')
    else:
        return packet['errcode'] + packet['errmsg'] + '\x00'


def _build_oack(packet):
    for opt, val in packet['options'].iteritems():
        if '\x00' in opt or '\x00' in val:
            raise PacketError('null byte in option/value')
    return '\x00'.join(elem for pair in packet['options'].iteritems() for elem in pair) + '\x00'


_BUILD_MAP = {
    OP_DATA: _build_data,
    OP_ERR: _build_error,
    OP_OACK: _build_oack,
}

def build_dgram(packet):
    """Return a datagram (string) from a packet objet (a dictionary).
    
    Raise KeyError if a key is missing from the packet object. A PacketError
    is raised if the datagram can't be build (invalid field in the packet).
    
    Look at parse_dgram for the keys that must be in the packet objects.
    
    Only OACK, DATA and ERROR packet are supported.
    
    """
    opcode = packet['opcode']
    try:
        fct = _BUILD_MAP[opcode]
    except KeyError:
        raise PacketError('invalid opcode')
    else:
        return opcode + fct(packet)


def err_packet(errcode, errmsg=''):
    """Return a new error packet.
    
    errcode is a 2-byte string and errmsg is a NVT ASCII string.
    
    """
    return {'opcode': OP_ERR, 'errcode': errcode, 'errmsg': errmsg}

def data_packet(blk_no, data):
    """Return a new data packet.
    
    blk_no is a 2-byte string and data is a string.
    
    """
    return {'opcode': OP_DATA, 'blkno': blk_no, 'data': data}

def oack_packet(options):
    """Return a new option acknowledgement packet.
    
    Options is a dictionary of option/value.
    
    """
    return {'opcode': OP_OACK, 'options': options}
