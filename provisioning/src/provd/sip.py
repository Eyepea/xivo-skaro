# -*- coding: UTF-8 -*-

"""Minimalist implementation of some elements of SIP (RFC3261/RFC3265) used
to send SIP NOTIFY request to SIP aware devices in an asynchronous way using
Twisted.

Authentication is supported. Only UDP transport is supported.

"""

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

# XXX doesn't accept multi-lines header line
# XXX unicode support ?

import logging
import re
import StringIO
from hashlib import md5
from os import urandom
from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol 

logger = logging.getLogger(__name__)


class HeaderFieldError(Exception):
    pass


class UnknownHeaderFieldError(HeaderFieldError):
    pass


class InvalidHeaderFieldError(HeaderFieldError):
    pass


class UnsupportedOperationError(Exception):
    pass


class InvalidMessageError(Exception):
    pass


class InvalidURIError(ValueError):
    pass


class NameValueParameter(object):
    def __init__(self, name, value):
        """
        name -- the parameter name (string)
        value -- the parameter value (string)
        """
        if not name:
            raise ValueError('zero length parameter name')
        if not value:
            raise ValueError('zero length parameter value')
        # XXX to lower() or not lower() ?
        self.name = name
        self.value = value
    
    def __str__(self):
        return '%s=%s' % (self.name, self.value)


class NameParameter(object):
    def __init__(self, name):
        if not name:
            raise ValueError('zero length parameter name')
        # XXX to lower() or not lower() ?
        self.name = name
    
    def __str__(self):
        return self.name


class Parameters(object):
    # XXX is it _always_ case-insensitive ?
    
    def __init__(self, params=()):
        """
        params -- an iterable of Parameter. A parameter is an object
          with a 'name' attribute.
        """
        self._params = dict((e.name, e) for e in params)
    
    def get(self, param_name):
        """
        Raise a KeyError if there's no parameter with a name of param_name.
        """
        return self._params[param_name]

    def __str__(self):
        result = StringIO.StringIO()
        for param in self._params.itervalues():
            result.write(';' + str(param))
        return result.getvalue()
    
    @staticmethod
    def _split_params(raw_params):
        # raw_params can either start with ';' or not
        if not raw_params:
            return []
        else:
            if raw_params[0] == ';':
                return raw_params[1:].split(';')
            else:
                return raw_params.split(';')

    @staticmethod
    def _parse_uri_parameter(raw_param):
        name, sep, value = raw_param.partition('=')
        if sep:
            return NameValueParameter(name, value)
        else:
            return NameParameter(name)
    
    @classmethod
    def parse(cls, raw_params):
        """
        raw_params -- a string representing parameters.
        
        Example:
          parse('')
          parse(';tranport=udp')
          parse(';transport=udp;user=phone')
        
        """
        return cls(map(cls._parse_uri_parameter,
                       cls._split_params(raw_params)))


class URI(object):
    """Represent a SIP or SIPS URI.
    
    Note that this class doesn't allow the specification of SIP request-header
    fields.
    
    """
    _PORT_MAP = {'sip': 5060, 'sips': 5061}
    
    def __init__(self, scheme, host, user=None, password=None, port=None, uri_params=Parameters()):
        self.scheme = scheme
        self.host = host
        self.user = user
        self.password = password
        if port is not None:
            self.port = port
        else:
            self.port = self._PORT_MAP[scheme]
        self.uri_params = uri_params
    
    @classmethod
    def new_sip_uri(cls, host, *args, **kwargs):
        return cls('sip', host, *args, **kwargs)
    
    @classmethod
    def new_sips_uri(cls, host, *args, **kwargs):
        return cls('sips', host, *args, **kwargs)
    
    def _append_scheme(self, result):
        result.write(self.scheme + ':')
    
    def _append_userinfo(self, result):
        if self.user is not None:
            result.write(self.user)
            if self.password is not None:
                result.write(':' + self.password)
            result.write('@')
    
    def _append_hostport(self, result):
        result.write(self.host)
        if self.port is not None:
            result.write(':' + str(self.port))
    
    def _append_uri_params(self, result):
        if self.uri_params is not None:
            result.write(str(self.uri_params))
    
    def __str__(self):
        result = StringIO.StringIO()
        self._append_scheme(result)
        self._append_userinfo(result)
        self._append_hostport(result)
        self._append_uri_params(result)
        return result.getvalue()
    
    @classmethod
    def _parse_scheme(cls, raw_uri, idx):
        # Return (scheme, idx)
        sep_idx = raw_uri.find(':', idx)
        if sep_idx == -1:
            raise InvalidURIError()
        scheme = raw_uri[idx:sep_idx]
        next_idx = sep_idx + 1
        if scheme not in ('sip', 'sips'):
            raise InvalidURIError('invalid scheme')
        return scheme, next_idx
    
    @classmethod
    def _parse_userinfo(cls, raw_uri, idx):
        # Return (user, password, idx)
        user = None
        password = None
        sep_idx = raw_uri.find('@', idx)
        if sep_idx != -1:
            next_idx = sep_idx + 1
            userinfo = raw_uri[idx:sep_idx]
            sep_idx = userinfo.find(':')
            if sep_idx == -1:
                user = userinfo
            else:
                user = userinfo[:sep_idx]
                password = userinfo[sep_idx + 1:]
            assert user is not None
            if not user:
                raise InvalidURIError('zero length user is not accepted')
        else:
            next_idx = idx
        return user, password, next_idx
    
    @classmethod
    def _parse_hostport(cls, raw_uri, idx):
        # Return (host, port, idx)
        port = None
        sep_idx = raw_uri.find(';', idx)
        if sep_idx == -1:
            next_idx = len(raw_uri)
        else:
            next_idx = sep_idx
        sep_idx = raw_uri.find(':', idx, next_idx)
        if sep_idx == -1:
            host = raw_uri[idx:next_idx]
        else:
            host = raw_uri[idx:sep_idx]
            port = raw_uri[sep_idx + 1:next_idx]
            port = int(port)
        return host, port, next_idx
    
    @classmethod
    def _parse_uri_params(cls, raw_uri, idx):
        # Return uri_params
        return Parameters.parse(raw_uri[idx:])
    
    @classmethod
    def parse(cls, raw_uri):
        idx = 0
        scheme, idx = cls._parse_scheme(raw_uri, idx)
        user, password, idx = cls._parse_userinfo(raw_uri, idx)
        host, port, idx = cls._parse_hostport(raw_uri, idx)
        uri_params = cls._parse_uri_params(raw_uri, idx)
        return cls(scheme, host, user, password, port, uri_params)


def new_crypto_id(n):
    """Return a random alphanumeric identifier with n bytes of randomness."""
    num = 0
    for byte in urandom(n):
        num <<= 8
        num += ord(byte)
    return "%x" % num


class CallIdHeaderField(object):
    """Call-ID header field.
    
    Instances of this class have the following attributes:
      id -- the call ID (string)
    
    """
    # Example:
    #   Call-ID: a84b4c76e66710@pc33.atlanta.com
    name = 'Call-ID'
    compact_name = 'i'
    
    def __init__(self, id=None):
        self.id = self.new_call_id() if id is None else id
    
    def __str__(self):
        return self.id
    
    @staticmethod
    def new_call_id():
        return new_crypto_id(16)
    
    @classmethod
    def parse(cls, raw_header_field_value):
        if not raw_header_field_value:
            raise InvalidHeaderFieldError('call-id can\'t be zero length')
        return cls(raw_header_field_value)


class ContactHeaderField(object):
    """Contact header field.
    
    Instances of this class have the following attributes:
      uri -- the URI of the contact
    
    """
    # Example:
    #   Contact: <sip:alice@pc33.atlanta.com>
    name = 'Contact'
    compact_name = 'm'
    
    def __init__(self, uri):
        self.uri = uri
    
    def __str__(self):
        return '<%s>' % self.uri
    
    @classmethod
    def parse(cls, raw_header_field_value):
        raise UnsupportedOperationError()


class ContentLengthHeaderField(object):
    """Content-Length header field.
    
    Instances of this class have the following attributes:
      length -- the content length (int)
    
    """
    # Example:
    #   Content-Length: 142
    name = 'Content-Length'
    compact_name = 'l'
    
    def __init__(self, length):
        self.length = length
    
    def __str__(self):
        return str(self.length)
    
    @classmethod
    def parse(cls, raw_header_field_value):
        try:
            length = int(raw_header_field_value)
        except ValueError:
            raise InvalidHeaderFieldError('"%s" is not an integer' % raw_header_field_value)
        if length < 0:
            raise InvalidHeaderFieldError('"%s" is not a positive integer' %
                                          raw_header_field_value)
        return cls(length)


class CSeqHeaderField(object):
    """CSeq header field.
    
    Instances of this class have the following attributes:
      number -- the 32-bit unsigned integer sequence number (int)
      method -- the request method (string)
    
    """
    # Example:
    #   CSeq: 314159 INVITE
    name = 'CSeq'
    compact_name = None
    
    def __init__(self, number, method):
        self.number = number
        self.method = method
    
    def __str__(self):
        return '%s %s' % (self.number, self.method)
    
    @classmethod
    def parse(cls, raw_header_field_value):
        try:
            raw_number, method = raw_header_field_value.split(' ')
        except ValueError:
            raise InvalidHeaderFieldError('invalid CSeq header "%s"' % raw_header_field_value)
        try:
            number = int(raw_number)
        except ValueError:
            raise InvalidHeaderFieldError('"%s" is not an integer' % raw_number)
        if number < 0:
            raise InvalidHeaderFieldError('"%s" is a negative integer' % number)
        return cls(number, method)


class EventHeaderField(object):
    """Event header field (see RFC3265).
    
    Instances of this class have the following attributes:
      event_type -- the type of the event (string)
    
    """
    # Example:
    #   Event: check-sync
    name = 'Event'
    compact_name = 'o'
    
    def __init__(self, event_type):
        self.event_type = event_type
    
    def __str__(self):
        return self.event_type
    
    @classmethod
    def parse(cls, raw_header_field_value):
        raise UnsupportedOperationError()


class _ToFromHeaderField(object):
    def __init__(self, uri, tag=None):
        self.uri = uri
        self.tag = tag
    
    def __str__(self):
        result = '<%s>' % self.uri
        if self.tag:
            result += ';tag=%s' % self.tag
        return result
    
    @staticmethod
    def new_tag_id():
        return new_crypto_id(4)
    
    @classmethod
    def parse(cls, raw_header_field_value):
        raise UnsupportedOperationError()


class FromHeaderField(_ToFromHeaderField):
    """From header field.
    
    Instances of this class have the following attributes:
      uri -- the URI
      tag -- the tag (string)
    
    """
    # Example:
    #   From: Alice <sip:alice@atlanta.com>;tag=1928301774
    name = 'From'
    compact_name = 'f'
    
    def __init__(self, uri, tag=None):
        tag = self.new_tag_id() if tag is None else tag
        _ToFromHeaderField.__init__(self, uri, tag)


class ToHeaderField(_ToFromHeaderField):
    """To header field.
    
    Instances of this class have the following attributes:
      uri -- the URI
      tag -- the tag (string)
    
    """
    # Example:
    #   To: Bob <sip:bob@biloxi.com>
    name = 'To'
    compact_name = 't'


class MaxForwardsHeaderField(object):
    """Max-Forwards header field.
    
    Instances of this class have the following attributes:
      number -- the remaining number of times this request message is allowed
          to be forwarded
    
    """
    # Example:
    #   Max-Forwards: 70
    name = 'Max-Forwards'
    compact_name = None
    
    def __init__(self, number=70):
        self.number = number
    
    def __str__(self):
        return str(self.number)
    
    @classmethod
    def parse(cls, raw_header_field_value):
        try:
            number = int(raw_header_field_value)
        except ValueError:
            raise InvalidHeaderFieldError('"%s" is not an integer' % raw_header_field_value)
        if number < 0:
            raise InvalidHeaderFieldError('"%s" is a negative integer' % number)
        return cls(number)


class SubscriptionStateHeaderField(object):
    """Subscription-State header field (see RFC3265).
    
    Instances of this class have the following attributes:
      state -- the state of the substriction (string)
    
    """
    # Example:
    #   Subscription-State: active
    name = 'Subscription-State'
    compact_name = None
    
    def __init__(self, state='active'):
        # state should be one of: active, pending or terminated
        self.state = state
    
    def __str__(self):
        return self.state
    
    @classmethod
    def parse(cls, raw_header_field_value):
        raise UnsupportedOperationError()


class ViaHeaderField(object):
    """Via header field.
    
    Instances of this class have the following attributes:
      id -- the call ID (string)
    
    Two instances of this class are equals if they have the same ID.
    
    """
    # Example:
    #   Via: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bK776asdhds
    name = 'Via'
    compact_name = 'v'
    
    def __init__(self, address, transport='udp', branch=None):
        """
        transport should be either udp or tcp.
        """
        self.address = address
        self.transport = transport
        self.branch = self.new_branch_id() if branch is None else branch
    
    def __str__(self):
        return "SIP/2.0/%s %s;branch=%s" % (self.transport.upper(),
                                            self.address,
                                            self.branch)
    
    @staticmethod
    def new_branch_id():
        # 'z9hG4bK' is a magic cookie defined in RFC3261
        return 'z9hG4bK' + new_crypto_id(8)
    
    @classmethod
    def parse(cls, raw_header_field_value):
        # does not accept multiple comma-separated via value
        try:
            proto, addr = raw_header_field_value.split(' ')
            transport = proto.split('/')[2].lower()
            address, raw_params = addr.split(';', 1)
            params = Parameters.parse(raw_params)
            branch = params.get('branch').value
        except (ValueError, IndexError, KeyError):
            raise InvalidHeaderFieldError(raw_header_field_value)
        return cls(address, transport, branch)


class AuthorizationHeaderField(object):
    """Authorization header field.
    
    Instances of this class have the following attributes:
      qop
      realm
      nonce
      cnonce
      username
      password
      method
      digest_uri
    
    Note that only Digest authentication is supported.
    
    """
    # Example:
    #   Digest username="4003",realm="xivo",nonce="6338a403",uri="sip:*10@xivo_proxies",algorithm=MD5,response="db22d7ef4a9443754cf2f20f4d3fd81f"
    name = 'Authorization'
    compact_name = None
    
    algorithm = 'MD5'
    nonce_count = '00000001'
    
    @staticmethod
    def _new_cnonce():
        return new_crypto_id(3)
    
    def __init__(self, method, digest_uri, username, password, auth_params):
        # auth_params must have the following keys:
        #   realm
        #   nonce
        if 'qop' in auth_params:
            qop_values = [v.strip().lower() for v in auth_params['qop'].split(',')]
            if 'auth' not in qop_values:
                raise ValueError('invalid qop value') 
            self.qop = 'auth'
        else:
            self.qop = None
        if 'algorithm' in auth_params:
            algorithm = auth_params['algorithm'].upper()
            if algorithm != 'MD5':
                raise ValueError('unsupported algorithm "%s"' % algorithm)
        self.realm = auth_params['realm']
        self.nonce = auth_params['nonce']
        
        self.cnonce = self._new_cnonce()
        self.username = username
        self.password = password
        self.method = method
        self.digest_uri = digest_uri
    
    def _compute_response(self):
        def H(x):
            return md5(x).hexdigest()
        A1 = '%s:%s:%s' % (self.username, self.realm, self.password)
        A2 = '%s:%s' % (self.method, self.digest_uri)
        HA1 = H(A1)
        HA2 = H(A2)
        if self.qop is None:
            response = H('%s:%s:%s' % (HA1, self.nonce, HA2))
        else:
            response = H('%s:%s:%s:%s:%s:%s' % (HA1, self.nonce, self.nonce_count,
                                             self.cnonce, self.qop, HA2))
        return response
    
    def _compute_header_value(self):
        value = 'Digest username="%s", realm="%s", nonce="%s", uri="%s", response=%s, algorithm=%s' % (
                                    self.username,
                                    self.realm,
                                    self.nonce,
                                    self.digest_uri,
                                    self._compute_response(),
                                    self.algorithm)
        if self.qop is not None:
            value += ', cnonce="%s", qop=%s, nc=%s' % (self.cnonce, self.qop, self.nonce_count)
        return value
    
    def __str__(self):
        return self._compute_header_value()
    
    @classmethod
    def parse(cls, raw_header_field_value):
        raise UnsupportedOperationError()


class WWWAuthenticateHeaderField(object):
    """WWW-Authenticate header field.
    
    Instances of this class have the following attributes:
      auth_params -- dictionary of auth parameters
    
    Note that only Digest authentication is supported.
    
    """
    # Example:
    #   Digest algorithm=MD5, realm="xivo", nonce="6338a403"
    #   Digest realm="xivo_proxies", nonce="715944b2", qop="auth", algorithm=md5
    name = 'WWW-Authenticate'
    compact_name = None
    
    _WWW_AUTH_RELAXED = re.compile(r"^(?:\s*(?:,\s*)?([^ \t\r\n=]+)\s*=\s*\"?((?<=\")(?:[^\\\"]|\\.)*?(?=\")|(?<!\")[^ \t\r\n,]+(?!\"))\"?)(.*)$")
    _UNQUOTE_PAIRS = re.compile(r'\\(.)')
    
    def __init__(self, auth_params):
        self.auth_params = auth_params
    
    def __str__(self):
        raise UnsupportedOperationError()
    
    @classmethod
    def parse(cls, raw_header_field_value):
        auth_scheme, remaining = raw_header_field_value.split(' ', 1)
        if auth_scheme.lower() != 'digest':
            raise InvalidHeaderFieldError('invalid auth scheme "%s"' % auth_scheme)
        match = cls._WWW_AUTH_RELAXED.search(remaining)
        auth_params = {}
        while match:
            if match and len(match.groups()) == 3:
                key, value, remaining = match.groups()
                auth_params[key.lower()] = cls._UNQUOTE_PAIRS.sub(r'\1', value)
            match = cls._WWW_AUTH_RELAXED.search(remaining)
        return cls(auth_params)


# XXX this is ugly and error prone...
_L_HEADER_FIELD_MAP = {}
_S_HEADER_FIELD_MAP = {}
def _build_header_field_maps():
    for cls in [AuthorizationHeaderField,
                CallIdHeaderField,
                ContactHeaderField,
                ContentLengthHeaderField,
                CSeqHeaderField,
                EventHeaderField,
                FromHeaderField,
                ToHeaderField,
                MaxForwardsHeaderField,
                SubscriptionStateHeaderField,
                ViaHeaderField,
                WWWAuthenticateHeaderField]:
        _L_HEADER_FIELD_MAP[cls.name.lower()] = cls
        if cls.compact_name:
            _S_HEADER_FIELD_MAP[cls.compact_name.lower()] = cls
_build_header_field_maps()


def _get_header_field_class(name):
    # Raise a UnknownHeaderFieldError if can't find the class
    try:
        return _L_HEADER_FIELD_MAP[name.lower()]
    except KeyError:
        try:
            return _S_HEADER_FIELD_MAP[name.lower()]
        except KeyError:
            raise UnknownHeaderFieldError('unknown header name "%s"' % name)


def build_header_line(header_field):
    """Return a formatted header line from a header field.
    
    >>> build_header_line(CallIdHeaderField('foo'))
    'Call-ID: foo'
    
    Raise an UnsupportedOperationError if building is not supported.
    
    """
    return "%s: %s" % (header_field.name, str(header_field))


def parse_header_line(header_line):
    """Parse a header line and return an header field.
    
    >>> parse_header_line('Call-ID: foo')
    <CallIdHeaderField object ...>
    
    Raise an InvalidHeaderFieldError if the header line is invalid.
    
    Raise an UnsupportedOperationError if the header line seems valid but
    we don't know how to parse it.
    
    """
    try:
        name, raw_header_field_value = header_line.split(':', 1)
    except ValueError:
        raise InvalidHeaderFieldError('no ":" separator in "%s"' % raw_header_field_value)
    name = name.rstrip()
    raw_header_field_value = raw_header_field_value.strip()
    header_field_class = _get_header_field_class(name)
    return header_field_class.parse(raw_header_field_value)


class Message(object):
    _FIRST_HEADERS = ('Via', 'Max-Forwards', 'To', 'From', 'Call-ID', 'CSeq', 'Contact')
    _LAST_HEADERS = ('Content-Type', 'Content-Length')
    
    def __init__(self, start_line, header_fields=()):
        self.start_line = start_line
        self.header_fields = dict((e.name, e) for e in header_fields)

    def set_header_field(self, header_field):
        self.header_fields[header_field.name] = header_field
    
    def build(self):
        result = StringIO.StringIO()
        def writeline(line):
            result.write(line)
            result.write('\r\n')
        writeline(self.start_line)
        
        header_fields = dict(self.header_fields)
        # reserve some headers for the end
        end_header_fields = {}
        for name in self._LAST_HEADERS:
            if name in header_fields:
                end_header_fields[name] = header_fields.pop(name)
        # write the first headers in a specific order
        for name in self._FIRST_HEADERS:
            if name in header_fields:
                header_field = header_fields.pop(name)
                writeline(build_header_line(header_field))
        # write the other headers
        for header_field in header_fields.itervalues():
            writeline(build_header_line(header_field))
        # write the last headers
        for name in self._LAST_HEADERS:
            if name in end_header_fields:
                end_header_fields = end_header_fields.pop(name)
                writeline(build_header_line(end_header_fields))
        result.write('\r\n')
        return result.getvalue()


def new_notify_message(uri, event_type):
    """Create and return a Message that is ready to be sent by a UAC.
    
    Note that some headers (Via, From, Contact) are missing, and it's the role
    of the UAC to add them.
    
    """
    start_line = 'NOTIFY %s SIP/2.0' % uri
    header_fields = []
    header_fields.append(MaxForwardsHeaderField())
    header_fields.append(ToHeaderField(uri))
    header_fields.append(CallIdHeaderField())
    header_fields.append(CSeqHeaderField(1, 'NOTIFY'))
    header_fields.append(EventHeaderField(event_type))
    header_fields.append(SubscriptionStateHeaderField())
    header_fields.append(ContentLengthHeaderField(0))
    return Message(start_line, header_fields)


def parse_message(raw_message):
    """Parse a SIP message and return a Message object.
    
    Note that the object returned hold only the valid headers that we know
    how to parse. Everything else is ignored.
    
    Raise an InvalidMessageError if the message doesn't look at all like a
    SIP message.
    
    """
    lines = raw_message.split('\r\n')
    try:
        start_line = lines[0]
    except IndexError:
        raise InvalidMessageError('zero-length message')
    header_fields = []
    for line in lines[1:]:
        if not line:
            # probably the last 'CRLF' line, we supose there's nothing left
            # after this
            break
        try:
            header_field = parse_header_line(line)
            header_fields.append(header_field)
        except (HeaderFieldError, UnsupportedOperationError):
            # ignore
            pass
    return Message(start_line, header_fields)


def parse_status_line(raw_status_line):
    """Parse the status line and return the status code.
    
    Raise a ValueError if the status line is invalid.
    
    """
    tokens = raw_status_line.split(' ', 2)
    version, raw_status_code = tokens[:2] 
    if version != 'SIP/2.0':
        raise ValueError('invalid version "%s"' % version)
    status_code = int(raw_status_code)
    if not 100 <= status_code < 1000:
        raise ValueError('invalid status code "%s"' % status_code)
    return status_code


class UDPUACProtocol(DatagramProtocol):
    """UAC using UDP as transport protocol.
    
    The deferred will fire once the transaction is completed. Note that there
    might be 2 transactions if we get an Unauthorized response first.
    
    """
    
    # FIXME this is a quick fix for Cisco SMB that need to wait
    #       for a certain amount of time before resending a request...
    _TIMEOUT = 25
    _UNAUTH_RETRY_TIMEOUT = 20
    
    def __init__(self, uri, message, credentials):
        self._uri = uri
        self._message = message
        self._credentials = credentials
        self._closed = False
        self._nb_try = 0
        self._timeout_timer = None
        self.deferred = Deferred()

    def _add_missing_header_fields(self):
        # Pre: a call to self.transport.connect must have been made
        local_endpoint = self.transport.getHost()
        local_ip, local_port = local_endpoint.host, local_endpoint.port
        local_ipport = '%s:%s' % (local_ip, local_port)
        src_uri = URI('sip', local_ip, port=local_port)
        self._message.set_header_field(ViaHeaderField(local_ipport, 'udp'))
        self._message.set_header_field(FromHeaderField(src_uri))
        self._message.set_header_field(ContactHeaderField(src_uri))
    
    def startProtocol(self):
        # XXX Note that host must be an IP address and not an hostname if
        #     we want to follow the recommandation from the twisted doc
        self.transport.connect(self._uri.host, self._uri.port)
        self._add_missing_header_fields()
        datagram = self._message.build()
        self._send_dgram(datagram)
    
    def _send_dgram(self, dgram):
        self.transport.write(dgram)
        self._set_timeout()
    
    def _close(self):
        if not self._closed:
            self._cancel_timeout()
            self.transport.stopListening()
            self._closed = True
    
    def _fail_and_close(self, msg):
        self.deferred.errback(Exception(msg))
        self._close()
    
    def _cancel_timeout(self):
        if self._timeout_timer:
            self._timeout_timer.cancel()
            self._timeout_timer = None
    
    def _on_timeout(self):
        self._timeout_timer = None
        self._fail_and_close('SIP timeout expired')
    
    def _set_timeout(self):
        from twisted.internet import reactor
        self._timeout_timer = reactor.callLater(self._TIMEOUT, self._on_timeout)
    
    def datagramReceived(self, data, (host, port)):
        self._cancel_timeout()
        try:
            message = parse_message(data)
        except InvalidMessageError:
            logger.warning('Invalid SIP message from %s (bad format)' % host)
            self._fail_and_close('Invalid SIP message')
        else:
            try:
                response_via = message.header_fields['Via']
            except KeyError:
                logger.warning('No Via header in SIP message from %s' % host)
                self._fail_and_close('No Via header')
            else:
                request_via = self._message.header_fields['Via']
                if response_via.branch != request_via.branch:
                    logger.warning('Received SIP message from an unknown transaction (received "%s", expecting "%s"' %
                                   response_via.branch, request_via.branch)
                    self._fail_and_close('Unknown SIP transaction')
                else:
                    # parse status line
                    try:
                        status_code = parse_status_line(message.start_line)
                    except ValueError:
                        logger.warning('Unable to parse status line "%s"' % message.start_line) 
                        self._fail_and_close('Invalid status line')
                    else:
                        if 100 <= status_code < 200:
                            logger.info('Received provisional response "%s", waiting for final response' % status_code)
                            self._set_timeout()
                        elif status_code == 401 and self._nb_try < 1 and self._credentials:
                            username, password = self._credentials
                            logger.info('Received 401 response, trying to authenticate')
                            self._nb_try += 1
                            auth_params = message.header_fields['WWW-Authenticate'].auth_params
                            method = self._message.start_line.split()[0]
                            auth = AuthorizationHeaderField(method, self._uri, username, password, auth_params)
                            self._message.set_header_field(auth)
                            self._message.header_fields['Via'].branch = ViaHeaderField.new_branch_id()
                            datagram = self._message.build()
                            logger.debug('Sending next message in %s seconds' % self._UNAUTH_RETRY_TIMEOUT)
                            from twisted.internet import reactor
                            reactor.callLater(self._UNAUTH_RETRY_TIMEOUT, self._send_dgram, datagram)
                        else:
                            logger.info('Received final response "%s", firing callback' % status_code)
                            self.deferred.callback(status_code)
                            self._close()


def _send_notify_udp(uri, message, credentials):
    protocol = UDPUACProtocol(uri, message, credentials)
    from twisted.internet import reactor
    reactor.listenUDP(0, protocol)
    return protocol.deferred


def send_notify(uri, event_type, credentials=None):
    """Do a SIP NOTIFY request and return a callback that will fire with the
    status code of the response.
    
    credentials is a tuple (username, password), or None.
    
    Note that only UDP request are supported currently.
    
    """
    message = new_notify_message(uri, event_type)
    uri_params = uri.uri_params
    try:
        transport = uri_params.get('transport')
    except KeyError:
        transport = 'udp'
    fun = {'udp': _send_notify_udp}.get(transport)
    return fun(uri, message, credentials)
