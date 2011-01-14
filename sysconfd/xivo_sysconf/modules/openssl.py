from __future__ import with_statement
"""commonconf module
"""
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010  Proformatique

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""

import os, os.path, logging
import magic
from M2Crypto import RSA, X509, SSL, m2, EVP

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_RW, CMD_R

class OpenSSL(object):
    """
    """
    def __init__(self):
        super(OpenSSL, self).__init__()
        #self.log = logging.getLogger('xivo_sysconf.modules.commonconf')

				#http_json_server.register(self.generate , CMD_RW, 
				#    safe_init=self.safe_init, 
				#    name='commonconf_generate')
        http_json_server.register(self.getSSLCertificates, CMD_R,
						safe_init=self.safe_init, name='openssl_getcertificats')
        http_json_server.register(self.getSSLCACertificates, CMD_R,
						name='openssl_getcacertificats')
        http_json_server.register(self.createSSLCACertificate, CMD_R,
						name='openssl_createcacertificat')
        
    def safe_init(self, options):
        self.certsdir       = options.configuration.get('openssl', 'certsdir')
        self.cadir          = options.configuration.get('openssl', 'cadir')

        self.m              = magic.open(magic.MAGIC_NONE)
        self.m.load('/usr/share/file/magic.mgc')
   
    def getSSLCertificates(self, args, options):
        return self._getSSLCertificates(self.certsdir)

    def getSSLCACertificates(self, args, options):
        return self._getSSLCertificates(self.cadir)

    def _getSSLCertificates(self, basedir):
        """get list of ssl certificates

				return dict:
				{
					'filename': type
				}
        """
        map_ = {
					'PEM certificate'         : 'certificate',
					'PEM certificate request' : 'request',
					'PEM RSA private key'     : 'private_key',
        }

        ret = {}
        for f in os.listdir(basedir):
            ret[f] = map_.get(self.m.file(os.path.join(basedir, f)), 'unknown')

        return ret

    def createSSLCACertificate(self, args, options):
        """
				>>> createSSLCACertificate({
						'des3'  : True,
						'size'i : 1024,
						'validity': 365,
						'password': 'abcd',
						'CN': 'FR',
						'ST': 'France',
						'L': 'Paris',
						'O': 'Proformatique',
						'OU': 'R&D',
						'CN': 'Guillaume Bour',
						'email': 'gbour@proformatique.com'

					}, {'name': 'proformatique'})
        """
        # Create private key
        rsa = RSA.gen_key(args.get('length', 1024), m2.RSA_F4)

        def _getpwd(*_args):
            return args.get('password', '')						
        rsa.save_key(os.path.join(self.cadir, options['name']+'.key'),
            cipher='aes_256_cbc', callback=_getpwd)

        # Create public key
        pubkey = EVP.PKey()        
        pubkey.assign_rsa(rsa)

        # Create request
        req = X509.Request()
        req.set_version(req.get_version())
        req.set_pubkey(pubkey)
        name = X509.X509_Name()
        name.CN = args.get('CN', 'FR')
        name.OU = args.get('OU', 'R&D Department')
        name.O  = args.get('O', 'Proformatique')
        name.L  = 'Puteaux'
        name.ST = 'Hauts-de-Seine'
        name.C  = 'FR'

        req.set_subject_name(name)
        req.sign(pubkey, 'md5')
       	req.save(os.path.join(self.cadir, options['name']+'.csr'))

        return True

    def createSSLCertificate(self, args, options):
        pass

openssl = OpenSSL()
