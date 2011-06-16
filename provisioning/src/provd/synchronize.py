# -*- coding: UTF-8 -*-

"""Synchronization services for devices."""

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2011  Proformatique <technique@proformatique.com>

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

import logging
import functools
import socket
import threading

logger = logging.getLogger(__name__)

_SYNC_SERVICE = None


class ISynchronizeService(object):
    """Interface for a synchronization service."""
    
    """A unique identifier for the type of synchronize service."""
    TYPE = "<type>"
    
    def __init__(self, *args, **kwargs):
        """Initialize this synchronize service."""
        raise Exception('This is an interface, not made to be instantiated')
    
    def close(self):
        """Close this synchronize service.
        
        Once this function has been successfully called once, it should be
        possible to call it again without any side-effects.
        
        """
        raise Exception('This is an interface, not made to be instantiated')


class AMIInteractionError(Exception):
    pass


class _RemoteSocketClosedError(Exception):
    pass


class _AsteriskAMIClient(object):
    # assertion are used in this class since this class is private to this module
    # Note that this is not thread safe.
    _TIMEOUT = 15.0
    
    def __init__(self, host, port, enable_tls, username, password):
        self._host = host
        self._port = port
        self._enable_tls = False
        self._username = username
        self._password = password
        
        self._sock = None
        self._buffer = ''
        self._action_id = 0
        self._action_ids = {}
        self.closed = False
    
    @property
    def connected(self):
        return self._sock is not None
    
    def _create_socket(self):
        # create a new socket and connect it to the AMI
        assert self._sock is None
        new_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            new_sock.settimeout(self._TIMEOUT)
            if self._enable_tls:
                import ssl
                new_sock = ssl.wrap_socket(new_sock)
                # TODO eventually takes a cert file in argument so that we can
                #      authenticate the server so we are not prone to MITM attack
            logger.info('Connecting to %s:%s...', self._host, self._port)
            new_sock.connect((self._host, self._port))
        except Exception, e:
            logger.error('Could not connect to %s: %s', self._host, e)
            new_sock.close()
            raise
        else:
            logger.info('Connected to %s', self._host)
            self._sock = new_sock
    
    def _close_socket(self):
        assert self._sock is not None
        self._sock.close()
        self._sock = None
        # clear actions ids
        self._actions_ids = {}
    
    def _new_action_id(self):
        action_id = str(self._action_id)
        self._action_id += 1
        return action_id
    
    def _send_packet(self, lines, add_action_id, reconnect):
        # Lines is a bunch of lines to send. Note that it should not contains
        # an action id, nor contain empty lines, i.e. it should be valid...
        # Note: lines object will be modified
        if add_action_id:
            lines.append('ActionID: %s' % self._new_action_id())
        lines.append('\r\n')
        # check if we are connected
        if self._sock is None:
            if reconnect:
                self._login()
            else:
                raise Exception('Not connected and reconnect is False')
        assert self._sock is not None
        try:
            self._sock.sendall('\r\n'.join(lines))
        except socket.error, e:
            logger.warning('Error while sending packet: %s', e)
            self._close_socket()
            if reconnect:
                self._login()
                # XXX raise AMIInteractionError on error ?
                self._sock.sendall('\r\n'.join(lines))
            else:
                # XXX raise AMIInteractionError ?
                raise
    
    def _recv_packet(self, action_id):
        # Receive the next packets until a packet with the given action id is
        # found and return it. If action_id is none, just read the next packets.
        assert self._sock is not None
        while action_id not in self._action_ids:
            while True:
                buffer = self._sock.recv(2048)
                if not buffer:
                    # empty buffer means the remote socket was closed
                    self._close_socket()
                    # XXX good exception to raise ?
                    raise _RemoteSocketClosedError('remote socket closed')
                self._buffer += buffer
                if '\r\n\r\n' in self._buffer:
                    break
            
            splitted_buffer = self._buffer.split('\r\n\r\n')
            self._buffer = splitted_buffer[-1]
            packets = splitted_buffer[:-1]
            
            for packet in packets:
                lines = packet.split('\r\n')
                for line in lines:
                    if line.startswith('ActionID:'):
                        action_id = int(line.split(':', 1)[1].lstrip())
                        self._action_ids[action_id] = lines
                        break
            
            if action_id is None:
                break
        
        return self._action_ids.pop(action_id, None)
    
    def _build_command_lines(self, action, args):
        lines = ['Action: %s' % action]
        for k, v in args:
            lines.append('%s: %s' % (k, v))
        return lines
    
    def _send_command(self, action, args=[], add_action_id=True, reconnect=True):
        # Build a packet from a command and sent it
        lines = self._build_command_lines(action, args)
        self._send_packet(lines, add_action_id, reconnect)
    
    def _get_value(self, key, lines):
        search_key = key + ':'
        for line in lines:
            if line.startswith(search_key):
                return line.split(':', 1)[1].lstrip()
        raise ValueError('No lines with key "%s" in: %s' % (key, lines))
    
    def _login(self):
        # Note that a failed login will yield a socket deconnection, i.e. it's
        # not possible to be connected yet not logged in
        assert self._sock is None
        self._create_socket()
        logger.info('Logging in to %s', self._host)
        aid = self._send_command('Login',
                                 [('Username', self._username),
                                  ('Secret', self._password)],
                                 reconnect=False)
        response_lines = self._recv_packet(aid)
        if self._get_value('Response', response_lines) != 'Success':
            self._close_socket()
            raise AMIInteractionError('Incorrect AMI username/password')
    
    def _logoff(self):
        assert self._sock is not None
        self._send_command('Logoff', add_action_id=False)
        
    def close(self):
        if not self.closed:
            if self._sock is not None:
                self._logoff()
                self._close_socket()
            self.closed = True
    
    def sip_notify(self, ip, event):
        aid = self._send_command('SIPnotifyprovd',
                                 [('PeerIP', ip.encode('ascii')),
                                  ('Variable', 'Event=%s' % event.encode('ascii'))])
        response_lines = self._recv_packet(aid)
        if self._get_value('Response', response_lines) != 'Success':
            raise AMIInteractionError('SIPnotifyprovd returned error: %s' %
                                      self._get_value('Message', response_lines))
    
    def sccp_reset(self, device_name):
        aid = self._send_command('SCCPDeviceRestart',
                                 [('Devicename', device_name),
                                  ('Type', 'reset')])
        response_lines = self._recv_packet(aid)
        if self._get_value('Response', response_lines) != 'Success':
            raise AMIInteractionError('SIPnotifyprovd returned error: %s' %
                                      self._get_value('Message', response_lines))
    
    def __repr__(self):
        return '<_AsteriskAMIClient to %s:%s (conneted, %s)>' % \
                (self._host, self._port, self._sock is not None)


def _asterisk_ami_sync_lock(fun):
    # to be used on methods that require locking of the AsteriskAMISynchronizeService class
    @functools.wraps(fun)
    def aux(self, *args, **kwargs):
        self._lock.acquire()
        try:
            return fun(self, *args, **kwargs)
        finally:
            self._lock.release()
    return aux


class AsteriskAMISynchronizeService(object):
    TYPE = 'AsteriskAMI'
    
    def __init__(self, servers):
        """
        servers is a list of dictionary, where each dictionary describe a server
        (i.e. an AMI) to connect to, with the following keys:
        - host
        - port (optional, default to 5038)
        - username
        - password
        - enable_tls (optional, default to false)
        
        Note that it's not an error if we are not able to connect to a server,
        we'll try to reconnect to it later.
        
        """
        self._lock = threading.Lock()
        self._clients = []
        for server in servers:
            client = _AsteriskAMIClient(server['host'],
                                        server.get('port', 5038),
                                        server.get('enable_tls', False),
                                        server['username'],
                                        server['password'])
            self._clients.append(client)
        self._closed = False
    
    @_asterisk_ami_sync_lock
    def close(self):
        if not self._closed:
            for client in self._clients:
                client.close()
            self._closed = True
    
    def _do_sip_notify(self, ip, event, recurse):
        for client in self._clients:
            try:
                client.sip_notify(ip, event)
            except AMIInteractionError, e:
                logger.debug('Interaction error for client %s: %s', client, e)
            except _RemoteSocketClosedError, e:
                if recurse:
                    self._do_sip_notify(ip, event, False)
                    return
                else:
                    raise
            except Exception, e:
                logger.info('Could not send sip_notify to %s: %s', client, e, exc_info=True)
            else:
                return
        raise AMIInteractionError('all AMI server returned false')
    
    @_asterisk_ami_sync_lock
    def sip_notify(self, ip, event):
        return self._do_sip_notify(ip, event, True)
    
    def _do_sccp_reset(self, device_name, recurse):
        for client in self._clients:
            try:
                client.sccp_reset(device_name)
            except AMIInteractionError, e:
                logger.debug('Interaction error for client %s: %s', client, e)
            except _RemoteSocketClosedError, e:
                if recurse:
                    self._do_sccp_reset(device_name, False)
                    return
                else:
                    raise
            except Exception, e:
                logger.info('Could not send sccp_reset to %s: %s', client, e)
            else:
                return
        raise AMIInteractionError('all AMI server returned false')
    
    @_asterisk_ami_sync_lock
    def sccp_reset(self, device_name):
        return self._do_sccp_reset(device_name, True)


def register_sync_service(sync_service):
    """Register a synchronize service globally."""
    logger.info('Registering synchronize service: %s', sync_service)
    global _SYNC_SERVICE
    _SYNC_SERVICE = sync_service


def unregister_sync_service():
    """Unregister the global synchronize service.
    
    This is a no-op if there was no register service registered.
    
    If a synchronize service was registered, this function will
    call its close method.
    
    """
    global _SYNC_SERVICE
    if _SYNC_SERVICE is not None:
        logger.info('Unregistering synchronize service: %s', _SYNC_SERVICE)
        _SYNC_SERVICE.close()
        _SYNC_SERVICE = None
    else:
        logger.info('No synchronize service registered')


def get_sync_service():
    """Return the globally registered synchronize service or None if no
    synchronize service has been registered.
    
    """
    return _SYNC_SERVICE
