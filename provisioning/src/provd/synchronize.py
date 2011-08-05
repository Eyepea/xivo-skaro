# -*- coding: UTF-8 -*-

"""Synchronization services for devices."""

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

import collections
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


class AMIError(Exception):
    pass


class _RemoteSocketClosedError(Exception):
    pass


class _LowLevelAMIClient(object):
    """    
    Once an instance of this class raise a _RemoteSocketClosedError, you
    should call its close method and not reuse the object.
    
    """
    def __init__(self, host, port=5038, enable_tls=False, timeout=15):
        """
        Raise a socket.error if we weren't unable to connect to the AMI
        server.
        
        """
        self._host = host
        self._buffer = ''
        self._recv_msg_queue = collections.deque()
        self._sock = self._new_connected_socket(port, enable_tls, timeout)
    
    def _new_connected_socket(self, port, enable_tls, timeout):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(timeout)
            if enable_tls:
                import ssl
                sock = ssl.wrap_socket(sock)
            logger.info('Connecting to AMI %s:%s...', self._host, port)
            sock.connect((self._host, port))
        except Exception, e:
            logger.error('Could not connect to AMI %s: %s', self._host, e)
            sock.close()
            raise
        else:
            logger.info('Connected to AMI %s', self._host)
            return sock
    
    def close(self):
        self._sock.close()
    
    def send_msg(self, msg):
        """Send an "AMI message", which is just a big string, not ending with
        an empty line.
        
        Raise a _RemoteSocketClosedError if we think the remote socket was
        closed. In this case, you should close this instance and create a
        new one if you want to reconnect.
        
        Raise a socket.timeout error if a timeout occurs.
        
        Raise a socket.error error if there's a socket error not related to
        the remote socket being closed.
        
        > client.send_msg("Action: Ping\r\nActionID: 1\r\n")
        
        """
        data = msg + '\r\n'
        try:
            self._sock.sendall(data)
        except socket.timeout:
            # socket.timeout is a child of socket.error
            raise
        except socket.error, e:
            logger.warning('Socket error while sending AMI message to %s: %s',
                           self._host, e)
            logger.warning('Assuming the remote socket was closed')
            raise _RemoteSocketClosedError('remote socket closed')
    
    def recv_msg(self):
        """Return an "AMI message". Note that the last '\r\n' is not included.
        
        > recv_msg()
        'Response: Success\r\nPing: Pong\r\nTimestamp: 1312554314.077034'
        
        Raise the same errors as send_msg.
        
        """
        if self._recv_msg_queue:
            return self._recv_msg_queue.popleft()
        
        while True:
            try:
                buffer = self._sock.recv(2048)
            except socket.timeout:
                raise
            except socket.error, e:
                logger.warning('Socket error while receiving data from %s: %s',
                               self._host, e)
                logger.warning('Assuming the remote socket was closed')
                raise _RemoteSocketClosedError('remote socket closed')
            else:
                if not buffer:
                    # empty buffer means the remote socket was closed
                    logger.warning('Empty string returned by recv from %s',
                                   self._host)
                    logger.warning('Assuming the remote socket was closed')
                    raise _RemoteSocketClosedError('remote socket closed')
                self._buffer += buffer
                if '\r\n\r\n' in self._buffer:
                    break
        
        splitted_buffer = self._buffer.split('\r\n\r\n')
        assert len(splitted_buffer) >= 2
        self._buffer = splitted_buffer[-1]
        self._recv_msg_queue.extend(splitted_buffer[1:-1])
        return splitted_buffer[0]


class _AMIClient(object):
    _TIMEOUT = 15
    
    def __init__(self, host, port, enable_tls, username, password):
        """
        Raise a socket.error if we could not connect to the server, or
        if we were connected but we had a timeout during the login.
        
        Raise a _RemoteSocketClosedError if we could connect but later on
        the connection was closed.
        
        Raise an AMIError if we could not login to the AMI.
        
        """
        self._host = host
        self._action_id = 0
        self._action_ids = {}
        self._ll_client = _LowLevelAMIClient(self._host, port, enable_tls,
                                             self._TIMEOUT)
        self._ll_client_closed = False
        try:
            self._login(username, password)
        except Exception:
            self._ll_client.close()
            raise
    
    def _new_msg(self, action, args=None):
        lines = ['Action: %s' % action]
        if args is not None:
            lines.extend('%s: %s' % (k, v) for (k, v) in args)
        lines.append('')
        return '\r\n'.join(lines)
    
    def _new_msg_with_action_id(self, action, args=None):
        action_id = str(self._action_id)
        self._action_id += 1
        
        action_id_tuple = ('ActionID', action_id)
        if args is not None:
            args = args + [action_id_tuple]
        else:
            args = [action_id_tuple]
        return action_id, self._new_msg(action, args)
    
    def _parse_msg(self, msg):
        # Return a dict where of keys/value
        #
        # NOTE: it doesn't handle multiple line with the same key, the last
        # value will be used.
        result = {}
        for line in msg.split('\r\n'):
            try:
                key, value = line.split(':', 1)
            except ValueError:
                # unpack error (at least in theory)
                logger.info('Invalid AMI line: %s', line)
            else:
                result[key] = value.lstrip()
        return result
    
    def _send_msg(self, msg):
        try:
            self._ll_client.send_msg(msg)
        except _RemoteSocketClosedError:
            self._ll_client.close()
            self._ll_client_closed = True
            raise
    
    def _recv_msg(self, action_id):
        while True:
            try:
                msg = self._ll_client.recv_msg()
            except _RemoteSocketClosedError:
                self._ll_client.close()
                self._ll_client_closed = True
                raise
            
            response_dict = self._parse_msg(msg)
            if response_dict.get('ActionID') == action_id:
                return response_dict
            else:
                logger.debug('Dropping message: %r', msg)
    
    def _check_response(self, response, action):
        if response.get('Response') != 'Success':
            raise AMIError('%s returned %s: %s' % (action,
                                                   response.get('Response', '<no resp>'),
                                                   response.get('Message', '<no msg>')))
    
    def _login(self, username, password):
        aid, msg = self._new_msg_with_action_id('Login',
                                                [('Username', username),
                                                 ('Secret', password)])
        self._send_msg(msg)
        response = self._recv_msg(aid)
        self._check_response(response, 'Login')
    
    def _logoff(self):
        msg = self._new_msg('Logoff')
        self._send_msg(msg)
    
    def close(self):
        if not self._ll_client_closed:
            try:
                self._logoff()
            except socket.error, e:
                logger.info('Error while logging off from AMI %s: %s', self._host, e)
            
            self._ll_client.close()
            self._ll_client_closed = True
    
    def sip_notify(self, ip, event):
        aid, msg = self._new_msg_with_action_id('SIPnotifyprovd',
                                                [('PeerIP', ip.encode('ascii')),
                                                 ('Variable', 'Event=%s' % event.encode('ascii'))])
        self._send_msg(msg)
        response = self._recv_msg(aid)
        self._check_response(response, 'SIPnotifyprovd')
    
    def sccp_reset(self, device_name):
        aid, msg = self._new_msg_with_action_id('SCCPDeviceRestart',
                                                [('Devicename', device_name.encode('ascii')),
                                                 ('Type', 'reset')])
        self._send_msg(msg)
        response = self._recv_msg(aid)
        self._check_response(response, 'SCCPDeviceRestart')


class _MaxReconnectionError(Exception):
    pass


class _ReconnectingAMIClient(object):
    """An AMI client that does transparent reconnecting."""
    def __init__(self, host, port, enable_tls, username, password, max_try=2):
        self._host = host
        self._port = port
        self._enable_tls = enable_tls
        self._username = username
        self._password = password
        self._max_try = max_try
        self._client = None
    
    def close(self):
        self._close_client()
    
    def _init_client(self):
        if self._client is None:
            self._client = _AMIClient(self._host, self._port, self._enable_tls,
                                      self._username, self._password)
    
    def _close_client(self):
        if self._client is not None:
            self._client.close()
            self._client = None
    
    def _do_client_method(self, method_name, args):
        for _ in xrange(self._max_try):
            try:
                self._init_client()
            except (_RemoteSocketClosedError, socket.error), e:
                    logger.warning('Error while creating client: %s', e)
            else:
                fun = getattr(self._client, method_name)
                try:
                    return fun(*args)
                except socket.timeout:
                    raise
                except (_RemoteSocketClosedError, socket.error), e:
                    logger.warning('AMI socket error: %s', e)
                    self._close_client()
        else:
            raise _MaxReconnectionError('giving up connection after %s try' %
                                        self._max_try)
    
    def sip_notify(self, ip, event):
        self._do_client_method('sip_notify', (ip, event))
    
    def sccp_reset(self, device_name):
        self._do_client_method('sccp_reset', (device_name,))
    
    def __repr__(self):
        return '<_ReconnectingAMIClient to %s:%s (connected, %s)>' % \
                (self._host, self._port, self._client is not None)


def _asterisk_ami_sync_lock(fun):
    # to be used on methods of the AsteriskAMISynchronizeService class that
    # require locking
    @functools.wraps(fun)
    def aux(self, *args, **kwargs):
        with self._lock:
            return fun(self, *args, **kwargs)
    return aux


class AsteriskAMISynchronizeService(object):
    # This class is thread safe
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
            client = _ReconnectingAMIClient(server['host'],
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
    
    def _do_client_method(self, method_name, args):
        for client in self._clients:
            fun = getattr(client, method_name)
            try:
                return fun(*args)
            except _MaxReconnectionError, e:
                logger.warning('Reconnection failed for client %s: %s', client, e)
            except socket.timeout:
                logger.warning('Socket timeout for client %s', client)
            except socket.error:
                logger.warning('Socket error for client %s: %s', e)
            except Exception, e:
                logger.warning('Error while doing %s%s via %s:',
                               method_name, args, client, exc_info=True)
        # going over all the AMI clients unsuccessfully means it's a failure 
        raise AMIError('all AMI servers returned failure')
    
    @_asterisk_ami_sync_lock
    def sip_notify(self, ip, event):
        self._do_client_method('sip_notify', (ip, event))
    
    @_asterisk_ami_sync_lock
    def sccp_reset(self, device_name):
        self._do_client_method('sccp_reset', (device_name,))


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
