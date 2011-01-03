#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""Small daemon program that is used to push DHCP status information into
the provisioning server.

DHCP status information is passed to it by the dxtorc application and this
information is then cached and sent if there was a change.

  dxtord -u user:pwd http://example.com:8000/dev_mgr

Where the URI point to the 'device manager' resource of the REST API of a
provisioning server. The username/password is used if the agent has to
authenticate to the provisioning server.

"""

try:
    import json
except ImportError:
    import simplejson as json
import logging
import os
import urllib2
import urlparse
import socket
import sys
from logging.handlers import SysLogHandler

PID_FILE         = '/var/run/dxtora.pid'
UNIX_SERVER_ADDR = '/var/run/dxtora.ctl'
PROV2_MIME_TYPE  = 'application/vnd.proformatique.prov2+json'

logger = logging.getLogger('dxtora')


class DHCPInfoSourceError(Exception):
    """Raised if there's an error while pulling DHCP information."""
    pass


class DHCPInfoSinkError(Exception):
    """Raised if there's an error while pushing DHCP information."""
    pass


class PidFileError(Exception):
    pass


class CachingDHCPInfoSink(object):
    """A destination for DHCP information objects.
    
    Cache DHCP information and trigger the next sink only if the info has
    changed.
    
    Note: its close method will call the close method of the next sink.
    
    """
    def __init__(self, next_sink):
        self._next_sink = next_sink
        self._cache = {}
    
    def close(self):
        self._next_sink.close()
    
    def _update_cache(self, dhcp_info):
        """Update the cache and return true if the cache has changed, else
        false.
        
        """
        ip = dhcp_info['ip']
        old_dhcp_info = self._cache.get(ip)
        if old_dhcp_info != dhcp_info:
            self._cache[ip] = dhcp_info
            return True
        else:
            return False
        
    def push(self, dhcp_info):
        """Send the dhcp_info object to the sink."""
        logger.info('Pushing DHCP info through cache')
        updated = self._update_cache(dhcp_info)
        if updated:
            logger.info('DHCP info not in cache -- pushing to next sink')
            self._next_sink.push(dhcp_info)
        else:
            logger.info('DHCP info in cache -- not pushing to next sink')


class StreamDHCPInfoSink(object):
    """A destination for DHCP information objects.
    
    Write the DHCP information as a string to a file object.
    
    Useful for testing/debugging...
    
    """
    def __init__(self, fobj):
        self._fobj = fobj
    
    def close(self):
        pass
    
    def push(self, dhcp_info):
        self._fobj.write(str(dhcp_info) + '\n')


class ProvServerDHCPInfoSink(object):
    """A destination for DHCP information objects.
    
    Send the DHCP information to a provisioning server via its REST API.
    
    """
    def __init__(self, base_uri, userpass=None):
        handlers = []
        if userpass:
            user, passwd = userpass.split(':', 1)
            pwd_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
            pwd_manager.add_password(None, base_uri, user, passwd)
            basic_handler = urllib2.HTTPBasicAuthHandler(pwd_manager)
            digest_handler = urllib2.HTTPDigestAuthHandler(pwd_manager)
            handlers.extend((basic_handler, digest_handler))
        self._opener = urllib2.build_opener(*handlers)
        self._base_uri = base_uri
        self._resource_uri = None
    
    def close(self):
        pass
    
    def _update_resource_uri(self):
        headers = {'Accept': PROV2_MIME_TYPE}
        request = urllib2.Request(self._base_uri, headers=headers)
        f = self._opener.open(request)
        try:
            content = json.load(f)
        finally:
            f.close()
            
        links = content[u'links']
        for link in links:
            if link[u'rel'] == u'dev.dhcpinfo':
                self._resource_uri = urlparse.urljoin(self._base_uri, link[u'href'])
        else:
            raise DHCPInfoSinkError('no link to DHCP info resource on base resource')
            
    def _do_push(self, dhcp_info, retry_on_404=True):
        if self._resource_uri is None:
            self._update_resource_uri()
        headers = {'Accept': '*/*', 'Content-Type': PROV2_MIME_TYPE}
        content = json.dumps(dhcp_info)
        request = urllib2.Request(self._base_uri, content, headers=headers)
        try:
            f = self._opener.open(request)
            f.read()
            f.close()
        except urllib2.HTTPError, e:
            code = e.code
            if 200 <= code <= 299:
                pass
            elif code == 404 and retry_on_404:
                self._update_resource_uri()
                self._do_push(dhcp_info, False)
            else:
                raise

    def push(self, dhcp_info):
        logger.info('Pushing DHCP info to prov server')
        try:
            self._do_push(dhcp_info)
        except DHCPInfoSinkError:
            raise
        except Exception, e:
            # XXX we are wrapping a bit too much
            raise DHCPInfoSinkError(e)


class UnixSocketDHCPInfoSource(object):
    """A source of DHCP information objects.
    
    Use a Unix datagram socket to get DHCP information.
    
    """
    def __init__(self, ctl_file):
        """Create a new source.
        
        Raise a socket.error exception if the socket can't be binded to
        ctl_file.
        
        """
        self._ctl_file = ctl_file
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            self._sock.bind(ctl_file)
        except socket.error:
            self._sock.close()
            raise
    
    def close(self):
        self._sock.close()
        _remove(self._ctl_file)
    
    def _check_op(self, op):
        # check that op is one of the 3 valid values
        if op not in ('commit', 'expiry', 'release'):
            raise DHCPInfoSourceError("invalid 'op' value: %s" % op)
    
    def _check_ip(self, ip):
        # check that ip is a dotted quad ip
        try:
            # Note that inet_aton accept strings with less than three dots.
            socket.inet_aton(ip)
        except socket.error:
            raise DHCPInfoSourceError("invalid 'ip' value: %s" % ip)
    
    def _check_mac(self, mac):
        # check that mac is a lowercase, colon separated mac
        # TODO if we really care
        pass
    
    def _check_dhcp_opts(self, dhcp_opts):
        # check that dhcp_opts is a sequence of valid dhcp_opt
        for dhcp_opt in dhcp_opts:
            if len(dhcp_opt) < 3:
                raise DHCPInfoSourceError("invalid 'dhcp_opt' value: too short")
            try:
                num = int(dhcp_opt[:3], 10)
            except ValueError:
                raise DHCPInfoSourceError("invalid 'dhcp_opt' value: not int")
            else:
                if not 0 <= num <= 255:
                    raise DHCPInfoSourceError("invalid 'dhcp_opt' value: invalid code")
    
    def _decode(self, data):
        """Takes the raw data from a request and return an dhcp_info
        dict ('op', 'ip', 'mac' and 'dhcp_opts').
        
        """
        lines = filter(None, data.split('\n'))
        dhcp_info = {}
        def check_and_add(key, value):
            check_fun = getattr(self, '_check_' + key)
            # next line raise an UpdateRawDataError if value is invalid
            check_fun(value)
            dhcp_info[key] = value
        try:
            check_and_add('op', lines[0])
            check_and_add('ip', lines[1])
            if dhcp_info['op'] == 'commit':
                check_and_add('mac', lines[2])
                check_and_add('dhcp_opts', lines[3:])
        except IndexError, e:
            raise DHCPInfoSourceError(e)
        else:
            return dhcp_info
    
    def pull(self):
        """Get a dhcp_info object from the source.
        
        Note: this is a blocking call.
        
        """
        logger.info('Pulling DHCP info from unix socket')
        data = self._sock.recvfrom(2048)[0]
        dhcp_info = self._decode(data)
        return dhcp_info


class Agent(object):
    """An agent that reads DHCP info from a source and send it to a sink in
    a loop.
    
    """
    def __init__(self, source, sink):
        """Create an agent."""
        self._source = source
        self._sink = sink
    
    def run(self):
        """Run the agent in loop."""
        while True:
            try:
                dhcp_info = self._source.pull()
                logger.info("Pulled DHCP info: (%(op)s, %(ip)s)", dhcp_info)
                self._sink.push(dhcp_info)
            except DHCPInfoSourceError, e:
                logger.error('Error while pulling info from source: %s', e)
            except DHCPInfoSinkError, e:
                logger.error('Error while pushing info to sink: %s', e)
            except Exception, e:
                logger.exception('Unspecified exception')


class PidFile(object):
    def _create_pid_file(self):
        pid = os.getpid()
        tmp_pid_file = self._pid_file + '.' + str(pid)
        try:
            fpid = open(tmp_pid_file, 'w')
        except EnvironmentError, e:
            raise PidFileError("couldn't create tmp pid file: %s" % e)
        else:
            try:
                fpid.write("%s\n" % pid)
            finally:
                fpid.close()
            try:
                os.link(tmp_pid_file, self._pid_file)
            except EnvironmentError, e:
                raise PidFileError("couldn't create pid file: %s" % e)
            finally:
                os.unlink(tmp_pid_file)
    
    def __init__(self, pid_file):
        self._pid_file = pid_file
        self._create_pid_file()

    def _remove_pid_file(self):
        _remove(self._pid_file)
        
    def close(self):
        self._remove_pid_file()


def _remove(file):
    # remove the file if present in a way that doesn't modify the stack
    # trace and doesn't raise an exception
    try:
        pass
    finally:
        try:
            os.remove(file)
        except EnvironmentError:
            pass


def _daemonize():
    try:
        pid = os.fork()
        if pid != 0:
            os._exit(0)
    except OSError, e:
        logger.exception("first fork() failed: %d (%s)", e.errno, e.strerror)
        sys.exit(1)
    
    os.chdir("/")
    os.setsid()
    os.umask(0)
    
    try:
        pid = os.fork()
        if pid != 0:
            os._exit(0)
    except OSError, e:
        logger.exception("second fork() failed: %d (%s)", e.errno, e.strerror)
        sys.exit(1)
    
    devnull_fd = os.open(os.devnull, os.O_RDWR)
    try: 
        for fd in (0, 1, 2):
            os.dup2(devnull_fd, fd)
    finally:
        os.close(devnull_fd)


def _sig_handler(signum, frame):
    raise SystemExit()


def main():
    import optparse
    import signal

    parser = optparse.OptionParser()
    parser.add_option('-u', '--user', dest='user',
                      help='user name and password for server authentication')
    parser.add_option('-f', '--foreground', action='store_true', dest='foreground',
                      help="don't daemonize")
    opt, args = parser.parse_args()
    
    logger.setLevel(logging.INFO)
    if opt.foreground:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(filename)s:%(lineno)3d - %(name)s: %(message)s"))
        logger.addHandler(handler)
    else:
        handler = SysLogHandler('/dev/log', SysLogHandler.LOG_DAEMON)
        handler.setFormatter(logging.Formatter("dxtora[%(process)d]: %(message)s"))
        logger.addHandler(handler)

    if len(args) != 1:
        print >>sys.stderr, 'error: need 1 argument (%d given)' % len(args)
        sys.exit(1)
    base_uri = args[0]
    
    source = UnixSocketDHCPInfoSource(UNIX_SERVER_ADDR)
    try:
        sink = CachingDHCPInfoSink(ProvServerDHCPInfoSink(base_uri, opt.user))
        #sink = StreamDHCPInfoSink(sys.stderr)
        try:
            if not opt.foreground:
                _daemonize()
            pidfile = PidFile(PID_FILE)
            try:
                signum = signal.SIGTERM
                old_handler = signal.signal(signum, _sig_handler)
                try:
                    agent = Agent(source, sink)
                    agent.run()
                finally:
                    signal.signal(signum, old_handler)
            finally:
                pidfile.close()
        finally:
            sink.close()
    finally:
        source.close()


if __name__ == '__main__':
    main()
