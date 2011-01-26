"""A TFTP server implementation with twisted.

The implementation is not totally RFC1350 (The TFTP protocol) and
RFC2347 (TFTP Option Extension) compliant, but is enough close to
it so that you might not care.

Things to note:
- only read request (RRQ) are supported. There is no support for write
  request (WRQ) as for now.
- netascii mode is not supported -- only octet mode is.
- mail mode is, of course, not supported, since it's deprecated.
- support the blksize option (RFC2348).
- doesn't handle gracefully the case where you want to transfer a file
  larger than what the TFTP protocol permits, which is 32 MiB if you
  are using the standard block size. If you try transferring such a file,
  the transfer will eventually fail from a block number desynchronization.
  Ideally, this should be detected at the start of the transfer instead
  of after sending 32 MiB.
- it's not using an adaptive timeout.
- although it would be theorically possible to run the TFTP service on
  a different datagram service than UDP, currently it is not because
  of a hard-coded call to reactor.listenUDP in the code after a request
  is accepted.

"""

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

from prov2.servers.tftp.proto import TFTPProtocol
from prov2.servers.tftp.service import *
