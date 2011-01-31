# -*- coding: UTF-8 -*-

"""Manage the transfer between two host."""

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

import struct
import logging

from twisted.internet.protocol import DatagramProtocol
from prov2.servers.tftp.packet import *

# TODO RFC1122 says we must use an adaptive timeout...
# TODO handle more gracefully the case where we want to send a file larger
#      than what the protocol permits
# TODO more logging statement

logger = logging.getLogger('tftp.connection')


class _NoMoreDatagramError(Exception):
    """Raised when there is no more datagram to send."""

_UINT16_STRUCT = struct.Struct('!H')

def _pack_from_uint16(n):
    # '_pack_from_uint16 = _UINT16_STRUCT.pack' is equivalent but less readable
    return _UINT16_STRUCT.pack(n)

def _unpack_to_uint16(string):
    return _UINT16_STRUCT.unpack(string)[0]


class _AbstractConnection(DatagramProtocol):
    """Represent a connection from the point of view of the server.
    
    The '_blk_no' instance attribute MUST be supplied in derived class.
    This value should be equal to the first value of the block number field.
    This value should be modify by the derived class such that it always
    reflect the block number we are waiting in the next ACK packet.
    we are waiting in the ACK packet.
      
    The '_next_dgram' method MUST be overridden in derived class. It should
    return the next datagram to send to the client. This is usually a DATA
    packet, but it could also be an OACK packet.
    
    The '_close' method MAY be overridden in derived class. It will be called
    once after the connection is closed, in any circumstances.
    
    """
    
    timeout = 3
    max_retries = 4
    
    def __init__(self, addr):
        """Create a new connection with a remote host.
        
        addr is the address of the remote host.
        
        """
        self._addr = addr
        self._closed = False
        self._dup_ack = False
        self._last_dgram = None
        self._retry_cnt = 0
        self._timeout_timer = None
        
    def _close(self):
        """Close this connection.
        
        This is the right place to do cleanup and will be called once and only
        once. MAY be overridden in derived class. 
        """
        pass
        
    def _next_dgram(self):
        """Return the next datagram to send to the remote host.
        
        Must be overridden in derived class.
        """
        raise NotImplementedError('Must be implemented in derived class')
    
    def __do_close(self):
        """Cleanup and make sure self._close is called once."""
        if not self._closed:
            logger.debug('Closing this connection')
            self._cancel_timeout()
            self._close()
            self._closed = True
            
    def _cancel_timeout(self):
        if self._timeout_timer:
            logger.debug('Cancelling the timeout')
            self._retry_cnt = 0
            self._timeout_timer.cancel()
            self._timeout_timer = None
    
    def _set_timeout(self):
        logger.debug('Setting the timeout with delay %s', self.timeout)
        from twisted.internet import reactor
        self._timeout_timer = reactor.callLater(self.timeout, self._timeout_expired)
    
    def _timeout_expired(self):
        logger.info('Timeout has expired with current retry count %s', self._retry_cnt)
        self._retry_cnt += 1
        if self._retry_cnt >= self.max_retries:
            self.__do_close()
        else:
            self._send_last_dgram()
            
    def _send_dgram(self, dgram):
        self.transport.write(dgram, self._addr)
        self._set_timeout()
        
    def _send_next_dgram(self):
        logger.debug('Sending a new datagram')
        try:
            dgram = self._next_dgram()
        except _NoMoreDatagramError:
            logger.debug('No more datagram to send')
            self.__do_close()
        else:
            self._send_dgram(dgram)
            self._last_dgram = dgram
    
    def _send_last_dgram(self):
        logger.debug('Resending the last datagram')
        self._send_dgram(self._last_dgram)
            
    def _handle_wrong_tid(self, addr):
        dgram = build_dgram(err_packet(ERR_UNKNWN_TID, 'Unknown TID'))
        self.transport.write(dgram, addr)
    
    def _handle_invalid_dgram(self):
        """Called when a datagram sent by the the remote host could not be parsed."""
        dgram = build_dgram(err_packet(ERR_UNDEF, 'Invalid datagram'))
        self.transport.write(dgram, self._addr)
        self.__do_close()
        
    def _handle_illegal_pkt(self, errmsg='Illegal TFTP operation'):
        dgram = build_dgram(err_packet(ERR_ILL, errmsg))
        self.transport.write(dgram, self._addr)
        self.__do_close()
        
    def _handle_ack(self, pkt):
        blk_no = _unpack_to_uint16(pkt['blkno'])
        if blk_no == self._blk_no:
            logger.debug('Received ACK for the current packet')
            self._dup_ack = False
            self._cancel_timeout()
            self._send_next_dgram()
        elif blk_no == self._blk_no - 1:
            logger.debug('Received ACK for the last packet')
            if not self._dup_ack:
                self._dup_ack = True
                self._cancel_timeout()
                self._send_last_dgram()
            else:
                logger.debug('Duplicated ACK - ignoring')
        else:
            logger.debug('Received ACK with an illegal block number')
            self._handle_illegal_pkt('Illegal block number')
    
    def datagramReceived(self, dgram, addr):
        logger.debug('Datagram received')
        if not self._closed:
            if addr != self._addr:
                logger.info('Datagram received with wrong TID')
                self._handle_wrong_tid(addr)
            else:
                try:
                    pkt = parse_dgram(dgram)
                except PacketError:
                    logger.info('Received an invalid datagram')
                    self._handle_invalid_dgram('ACK packet')
                else:
                    if pkt['opcode'] == OP_ERR:
                        logger.info('Received an error packet')
                        self.__do_close()
                    elif pkt['opcode'] == OP_ACK:
                        self._handle_ack(pkt)
                    else:
                        logger.info('Received an unexpected packet - opcode %s', pkt['opcode'])
                        self._handle_illegal_pkt()
    
    def startProtocol(self):
        logger.debug('In startProtocol')
        self._send_next_dgram()

    def stopProtocol(self):
        logger.debug('In stopProtocol')
        self.__do_close()


class RFC1350Connection(_AbstractConnection):
    def __init__(self, addr, fobj):
        """Create a new RFC1350 connection.
        
        addr -- the address of the remote host.
        fobj -- a file-object that is going to be transmitted. This object will call its close method.
         
        """
        _AbstractConnection.__init__(self, addr)
        self._fobj = fobj
        self._blk_no = 0
    
    def _close(self):
        self._fobj.close()
        self.transport.stopListening()
        
    def _next_dgram(self):
        buf = self._fobj.read(512)
        if not buf:
            raise _NoMoreDatagramError()
        else:
            self._blk_no += 1
            dgram = build_dgram(data_packet(_pack_from_uint16(self._blk_no), buf))
            return dgram


class RFC2347Connection(_AbstractConnection):
    blksize = 512
    
    def __init__(self, addr, fobj, oack_dgram):
        """Create a new RFC2347 connection.
        
        addr -- the address of the remote host.
        fobj -- a file-object that is going to be transmitted. This object will call the close method.
        oack_dgram -- an option acknowledgement datagram
        
        """
        _AbstractConnection.__init__(self, addr)
        self._fobj = fobj
        self._oack_dgram = oack_dgram
        self._blk_no = -1
    
    def _close(self):
        self._fobj.close()
        self.transport.stopListening()
        
    def _next_dgram(self):
        if self._blk_no == -1:
            self._blk_no += 1
            return self._oack_dgram
        else:
            buf = self._fobj.read(self.blksize)
            if not buf:
                raise _NoMoreDatagramError()
            else:
                self._blk_no += 1
                dgram = build_dgram(data_packet(_pack_from_uint16(self._blk_no), buf))
                return dgram
