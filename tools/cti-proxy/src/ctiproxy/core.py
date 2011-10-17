# -*- coding: UTF-8 -*-

import json
import logging
import select
import socket
import sys
import time
from datetime import datetime

logger = logging.getLogger(__name__)


def _get_fmted_time():
    return datetime.now().strftime("%H:%M:%S.%f")


def _get_client_to_server_header():
    return "    %s Client > Server" % _get_fmted_time()


def _get_server_to_client_header():
    return "    %s Server > Client" % _get_fmted_time()


class BaseListener(object):
    def close(self):
        pass

    def connection_established(self):
        pass

    def connection_closed(self):
        pass

    def client_send(self, data):
        pass

    def server_send(self, data):
        pass


class ForwardListener(object):
    def __init__(self, listener):
        self._listener = listener

    def close(self):
        self._listener.close()

    def connection_established(self):
        self._listener.connection_established()

    def connection_closed(self):
        self._listener.connection_closed()

    def client_send(self, data):
        self._listener.client_send(data)

    def server_send(self, data):
        self._listener.server_send(data)


class NewlineSplitListener(ForwardListener):
    def __init__(self, listener):
        ForwardListener.__init__(self, listener)
        self._client_buf = ""
        self._server_buf = ""

    def client_send(self, data):
        buf = self._client_buf + data
        tokens = buf.split("\n")
        self._client_buf = tokens[-1]
        lines = tokens[:-1]
        for line in lines:
            self._listener.client_send(line)

    def server_send(self, data):
        buf = self._server_buf + data
        tokens = buf.split("\n")
        self._server_buf = tokens[-1]
        lines = tokens[:-1]
        for line in lines:
            self._listener.server_send(line)


class RawPrintListener(BaseListener):
    def client_send(self, data):
        print _get_client_to_server_header()
        print data

    def server_send(self, data):
        print _get_server_to_client_header()
        print data


class NoClientListener(ForwardListener):
    def client_send(self, data):
        pass


class NoServerListener(ForwardListener):
    def server_send(self, data):
        pass


class StatisticListener(BaseListener):
    """
    Since we are working at the application level, we can't know for sure the
    number of IP packets nor the size "at the wire" of any packets (which can
    be different depending on IP/TCP options used). This means only the
    application bytes count is accurate, all the others are estimated.
    
    """
    _ETH_IP_TCP_BYTES = 14 + 20 + 16

    def __init__(self):
        self.start_time = None
        self.stop_time = None
        self.client_pkts = 0
        self.client_app_bytes = 0
        self.server_pkts = 0
        self.server_app_bytes = 0

    def connection_established(self):
        self.start_time = time.time()

    def connection_closed(self):
        self.stop_time = time.time()

    def client_send(self, data):
        self.client_pkts += 1
        self.client_app_bytes += len(data)

    def server_send(self, data):
        self.server_pkts += 1
        self.server_app_bytes += len(data)

    @property
    def total_pkts(self):
        return self.client_pkts + self.server_pkts

    @property
    def total_app_bytes(self):
        return self.client_app_bytes + self.server_app_bytes

    @property
    def client_wire_bytes(self):
        return self.client_pkts * self._ETH_IP_TCP_BYTES + self.client_app_bytes

    @property
    def server_wire_bytes(self):
        return self.server_pkts * self._ETH_IP_TCP_BYTES + self.server_app_bytes

    @property
    def total_wire_bytes(self):
        return self.client_wire_bytes + self.server_wire_bytes

    @property
    def total_wire_overhead(self):
        try:
            return self.total_pkts * self._ETH_IP_TCP_BYTES / float(self.total_app_bytes)
        except ZeroDivisionError:
            return 0.0

    @property
    def running_time(self):
        try:
            return self.stop_time - self.start_time
        except TypeError:
            return 0.0

    @property
    def avg_pkts_per_seconds(self):
        try:
            return self.total_pkts / self.running_time
        except ZeroDivisionError:
            return 0.0

    @property
    def avg_app_bytes_per_seconds(self):
        try:
            return self.total_app_bytes / self.running_time
        except ZeroDivisionError:
            return 0.0

    @property
    def avg_wire_bytes_per_seconds(self):
        try:
            return self.total_wire_bytes / self.running_time
        except ZeroDivisionError:
            return 0.0

    def print_stats(self):
        print "Running time:\t\t", self.running_time
        print "Client app bytes:\t", self.client_app_bytes
        print "Server app bytes:\t", self.server_app_bytes
        print "Total app bytes:\t", self.total_app_bytes
        print "Avg app bytes/s:\t", self.avg_app_bytes_per_seconds
        print "==========="
        print "Client IP packets:\t", self.client_pkts
        print "Server IP packets:\t", self.server_pkts
        print "Total IP packets:\t", self.total_pkts
        print "Average IP packets/s:\t", self.avg_pkts_per_seconds
        print "==========="
        print "Client wire bytes:\t", self.client_wire_bytes
        print "Server wire bytes:\t", self.server_wire_bytes
        print "Total wire bytes:\t", self.total_wire_bytes
        print "Total headers overhead:\t", self.total_wire_overhead
        print "Average wire bytes/s:\t", self.avg_wire_bytes_per_seconds


class JsonDecoderListener(ForwardListener):
    def client_send(self, data):
        try:
            self._listener.client_send_msg(json.loads(data))
        except ValueError:
            self._listener.client_send_data(data)

    def server_send(self, data):
        try:
            self._listener.server_send_msg(json.loads(data))
        except ValueError:
            self._listener.server_send_data(data)


class BaseMsgListener(object):
    def close(self):
        pass

    def connection_established(self):
        pass

    def connection_closed(self):
        pass

    def client_send_msg(self, msg):
        pass

    def client_send_data(self, data):
        pass

    def server_send_msg(self, msg):
        pass

    def server_send_data(self, data):
        pass


class ForwardMsgListener(object):
    def __init__(self, listener):
        self._listener = listener

    def close(self):
        self._listener.close()

    def connection_established(self):
        self._listener.connection_established()

    def connection_closed(self):
        self._listener.connection_closed()

    def client_send_msg(self, msg):
        self._listener.client_send_msg(msg)

    def client_send_data(self, data):
        self._listener.server_send_msg(data)

    def server_send_msg(self, msg):
        self._listener.server_send_msg(msg)

    def server_send_data(self, data):
        self._listener.server_send_data(data)


class StripListener(ForwardMsgListener):
    def __init__(self, listener, elements):
        ForwardMsgListener.__init__(self, listener)
        self._elements = list(set(elements))

    def client_send_msg(self, msg):
        for e in self._elements:
            msg.pop(e, None)
        self._listener.client_send_msg(msg)

    def server_send_msg(self, msg):
        for e in self._elements:
            msg.pop(e, None)
        self._listener.server_send_msg(msg)


class IncludeListener(ForwardMsgListener):
    def __init__(self, listener, key, value):
        ForwardMsgListener.__init__(self, listener)
        self._key = key
        self._value = value

    def client_send_data(self, data):
        pass

    def client_send_msg(self, msg):
        if msg.get(self._key) == self._value:
            self._listener.client_send_msg(msg)

    def server_send_msg(self, msg):
        if msg.get(self._key) == self._value:
            self._listener.server_send_msg(msg)

    def server_send_data(self, data):
        pass


class PrintMsgListener(BaseMsgListener):
    def __init__(self, pretty_print=False):
        self._pretty_print = pretty_print

    def client_send_msg(self, msg):
        print _get_client_to_server_header()
        if self._pretty_print:
            json.dump(msg, sys.stdout, indent=4, sort_keys=True)
        else:
            json.dump(msg, sys.stdout, sort_keys=True)
        print

    def client_send_data(self, data):
        print _get_client_to_server_header()
        print data

    def server_send_msg(self, msg):
        print _get_server_to_client_header()
        if self._pretty_print:
            json.dump(msg, sys.stdout, indent=4, sort_keys=True)
        else:
            json.dump(msg, sys.stdout, sort_keys=True)
        print

    def server_send_data(self, data):
        print _get_server_to_client_header()
        print data


class FileWriterMsgListener(BaseMsgListener):
    def __init__(self, client_file, server_file):
        self._client_fobj = open(client_file, "wb")
        self._server_fobj = open(server_file, "wb")

    def close(self):
        self._client_fobj.close()
        self._server_fobj.close()

    def client_send_msg(self, msg):
        json.dump(msg, self._client_fobj, indent=4, sort_keys=True)
        self._client_fobj.write('\n')

    def client_send_data(self, data):
        self._client_fobj.write(data)
        self._client_fobj.write('\n')

    def server_send_msg(self, msg):
        json.dump(msg, self._server_fobj, indent=4, sort_keys=True)
        self._server_fobj.write('\n')

    def server_send_data(self, data):
        self._server_fobj.write(data)
        self._server_fobj.write('\n')


class _RemoteSocketClosedError(Exception):
    pass


class SocketProxy(object):
    _BUFSIZE = 4096

    def __init__(self, client_socket, server_socket, listener, timeout=None):
        """
        Note that the sockets are owned by the newly created instance.
        """
        self._client_socket = client_socket
        self._server_socket = server_socket
        self._listener = listener
        self._timeout = timeout
        self._asked_to_stop = False

    def start(self):
        """
        Return only if at least one side of the connection is closed (or if
        a socket error occurs) or the stop method is called and the timeout
        is not None.
        
        """
        logger.debug("Starting SocketProxy %s", self)
        try:
            self._listener.connection_established()
            self._do_start()
        except _RemoteSocketClosedError:
            pass
        finally:
            self._listener.connection_closed()
            self._client_socket.close()
            self._server_socket.close()

    def _do_start(self):
        self._client_socket.setblocking(0)
        self._server_socket.setblocking(0)
        client_buf = "" # buffer of data to send to client
        server_buf = "" # buffer of data to send to server
        while not self._asked_to_stop:
            # compute rlist and wlist
            rlist = []
            wlist = []
            if not client_buf and not server_buf:
                logger.debug("Empty buffers")
                rlist = [self._client_socket, self._server_socket]
                wlist = []
            elif not client_buf:
                assert server_buf
                logger.debug("Non-empty client buffer")
                rlist = []
                wlist = [self._server_socket]
            elif not server_buf:
                assert client_buf
                logger.debug("Non-empty server buffer")
                rlist = []
                wlist = [self._client_socket]
            else:
                assert client_buf and server_buf
                logger.debug("Non-empty buffers")
                rlist = []
                wlist = [self._client_socket, self._server_socket]

            r_rlist, r_wlist, _ = select.select(rlist, wlist, [], self._timeout)
            for cur_socket in r_wlist:
                if cur_socket == self._client_socket:
                    assert client_buf
                    logger.debug("Sending data to client")
                    try:
                        n = self._client_socket.send(client_buf)
                    except socket.error:
                        raise _RemoteSocketClosedError("send to client")
                    else:
                        client_buf = client_buf[n:]
                elif cur_socket == self._server_socket:
                    assert server_buf
                    logger.debug("Sending data to server")
                    try:
                        n = self._server_socket.send(server_buf)
                    except socket.error:
                        raise _RemoteSocketClosedError("send to server")
                    else:
                        server_buf = server_buf[n:]
                else:
                    raise AssertionError("cur_socket is: %r" % cur_socket)

            for cur_socket in r_rlist:
                if cur_socket == self._client_socket:
                    logger.debug("Receiving data from client")
                    try:
                        buf = self._client_socket.recv(self._BUFSIZE)
                    except socket.error:
                        raise _RemoteSocketClosedError("recv from client")
                    else:
                        if not buf:
                            raise _RemoteSocketClosedError("recv from client")
                        self._listener.client_send(buf)
                        server_buf += buf
                elif cur_socket == self._server_socket:
                    logger.debug("Receiving data from server")
                    try:
                        buf = self._server_socket.recv(self._BUFSIZE)
                    except socket.error:
                        raise _RemoteSocketClosedError("recv from server")
                    else:
                        if not buf:
                            raise _RemoteSocketClosedError("recv from server")
                        self._listener.server_send(buf)
                        client_buf += buf
                else:
                    raise AssertionError("cur_socket is: %r" % cur_socket)

    def stop(self):
        self._asked_to_stop = True


class IPv4ProxyEstablisher(object):
    def __init__(self, bind_address, server_address):
        self._server_address = server_address
        self._listen_socket = self._new_listen_socket(bind_address)

    def _new_listen_socket(self, address):
        lsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            lsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            lsocket.bind(address)
            lsocket.listen(2)
        except Exception:
            lsocket.close()
            raise
        return lsocket

    def close(self):
        self._listen_socket.close()

    def establish_connections(self):
        logger.info("Waiting for client connection")
        client_socket, addr = self._listen_socket.accept()
        logger.info("Client connection from %s", addr)
        try:
            server_socket = self._new_server_socket()
        except Exception, e:
            logger.error("Error while establishing server connection: %s", e)
            client_socket.close()
            raise
        else:
            return client_socket, server_socket

    def _new_server_socket(self):
        ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssocket.connect(self._server_address)
        logger.info("Server connection to %s", self._server_address)
        return ssocket
