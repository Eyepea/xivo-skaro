# -*- coding: utf8 -*-
from __future__ import with_statement
"""commonconf module
"""
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011 Proformatique, Guillaume Bour <gbour@proformatique.com>

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

import os, os.path, logging, time, random, shutil, glob
import magic
from M2Crypto import RSA, X509, SSL, m2, EVP, ASN1

from xivo import http_json_server
from xivo.http_json_server import HttpReqError
from xivo.http_json_server import CMD_RW, CMD_R

CIPHERS = {
	'aes'  : 'aes_128_cbc',
	'des'  : 'des_ede_cbc',
	'des3' : 'des_ede3_cbc',
	'idea' : 'idea_cbc'
}

DEFAULT_CIPHER = CIPHERS['aes']

class OpenSSL(object):
    """
    """
    def __init__(self):
        super(OpenSSL, self).__init__()
        #self.log = logging.getLogger('xivo_sysconf.modules.commonconf')

        http_json_server.register(self.listCertificates, CMD_R,
						name='openssl_listcertificates', safe_init=self.safe_init)
        http_json_server.register(self.listKeys, CMD_R,
						name='openssl_listkeys')
        http_json_server.register(self.getCertificateInfos, CMD_R,
						name='openssl_certificateinfos')
        http_json_server.register(self.createSSLCACertificate, CMD_RW,
						name='openssl_createcacertificate')
        http_json_server.register(self.createSSLCertificate, CMD_RW,
						name='openssl_createcertificate')
        http_json_server.register(self.deleteCertificate, CMD_R, name='openssl_deletecertificate')

    def safe_init(self, options):
        self.certsdir       = options.configuration.get('openssl', 'certsdir')
        if not os.path.exists(self.certsdir):
            os.makedirs(self.certsdir)

        self.m              = magic.open(magic.MAGIC_NONE)
        self.m.load('/usr/share/file/magic.mgc')


    def _keyfile(self, name):
        """private key"""
        return os.path.join(self.certsdir, name+'.key')

    def _crtfile(self, name):
        """certificate"""
        return os.path.join(self.certsdir, name+'.crt')

    def _pemfile(self, name):
        """private ket + certificate"""
        return os.path.join(self.certsdir, name+'.pem')

    def _pubfile(self, name):
        """pub key"""
        return os.path.join(self.certsdir, name+'.pub')


    def listCertificates(self, args, options):
        """Return list of available certificates

				"""
        certs = []
        for fname in glob.iglob(os.path.join(self.certsdir, '*.pem')):
            cert = X509.load_cert(fname)

            certs.append({
							'name'					 : os.path.basename(fname).rsplit('.',2)[0],
							'CA'             : cert.check_ca() == 1,
							'autosigned'     : str(cert.get_subject()) == str(cert.get_issuer()),
							'length'         : len(cert.get_pubkey().get_rsa()),
							'fingerprint'    : 'md5:'+cert.get_fingerprint(),
							'validity-end'   : cert.get_not_after().get_datetime().strftime("%Y/%m/%d %H:%M:%S %Z"),
							'path'           : fname,
						})

        return certs

    def listKeys(self, args, options):
        """Return list of available keys

					arguments:
						type (str, optional): 'both','private' or 'public', depending on wether
						you want to get all, private only or public only keys
        """
        keys = []; index = {}

        type = options.get('type','both')
        if type in ('both','private'):
            for fname in glob.iglob(os.path.join(self.certsdir, '*.key')):
                keys.append({
                  'name'             : os.path.basename(fname).rsplit('.',2)[0],
                  'path'             : fname,
                  'type'             : 'private',
                })

        if type in ('both','public'):
            for fname in glob.iglob(os.path.join(self.certsdir, '*.pub')):
                keys.append({
                  'name'             : os.path.basename(fname).rsplit('.',2)[0],
                  'path'             : fname,
                  'type'             : 'public',
                })

        return keys


    def getCertificateInfos(self, args, options):
        """Return informations about a certificate

					args:
						. certificate name

					returns
						a dictionary containing certificate informations
				
					>>> getCertificateInfos('wiki.proformatique.com')
						{
							'sn'             : 2445288...L
							'CA'             : 0
							'length'         : 4242,
							'fingerprint'    : 'md5:0000...'
							'validity-start' : '2011/04/14 13:04:26 UTC',
							'validity-end'   : '2012/12/12 12:12:12 UTC',
							'subject'        : {
							   'C': 'FR',
 		             'CN': 'wiki.proformatique.com',
     		         'L': 'Puteaux',
         		     'O': 'Proformatique',
	               'OU': 'R&D Department',
   		           'ST': 'France',
       		       'emailAddress': 'webmaster@proformatique.com'
							},
							'issuer'        : {
								 'C': 'FR',
		             'CN': '*',
    		         'L': 'Puteaux',
        		     'O': 'Proformatique',
            		 'OU': 'R&D Department',
		             'ST': 'France',
    		         'emailAddress': 'passe-partout@proformatique.com'
							},
							'extensions'     : {}
						}
        """
        print options, args
        if not os.path.exists(self._pemfile(options['name'])):
            raise HttpReqError(404, "%s certificate not found" % options['name'])

        cert = X509.load_cert(self._pemfile(options['name']))
        infos = {
						'sn'             : cert.get_serial_number(),
						'CA'             : cert.check_ca() == 1,
						'autosigned'     : str(cert.get_subject()) == str(cert.get_issuer()),
						'length'         : len(cert.get_pubkey().get_rsa()),
						'fingerprint'    : 'md5:'+cert.get_fingerprint(),
						'validity-start' : cert.get_not_before().get_datetime().strftime("%Y/%m/%d %H:%M:%S %Z"),
						'validity-end'   : cert.get_not_after().get_datetime().strftime("%Y/%m/%d %H:%M:%S %Z"),
						'path'           : self._pemfile(options['name'])
					}

        infos['subject'] = dict([(k, v) for (k, v) in [nid.split('=') for nid in 
					str(cert.get_subject()).split('/') if len(nid) > 0]])
        infos['issuer'] = dict([(k, v) for (k, v) in [nid.split('=') for nid in 
					str(cert.get_issuer()).split('/') if len(nid) > 0]])

        exts = {}
        for i in xrange(cert.get_ext_count()):
            e = cert.get_ext_at(i)
            exts[e.get_name()] = e.get_value()
        infos['extensions'] = exts

        return infos

    def _makekey(self, name, password='', keylen=1024, cipher=DEFAULT_CIPHER):
        """Create a RSA key.

					*private function*

					args:
						. name     : key name (filename will be 'name.key')
            . password : key password (if empty, key will be passwordless)
						. keylen   : private key size, in bits
						. cipher   : cipher used to encrypt key

					returns:
					  . the key
        """				
        # Create private key
        rsa = RSA.gen_key(keylen, m2.RSA_F4)

        def _getpwd(*_args):
            return password
				#NOTE: when empty password, need not to use a cipher, or generated key file is empty
        rsa.save_key(self._keyfile(name),
            cipher=cipher if len(password) > 0 else None,
						callback=_getpwd)

        rsa.save_pub_key(self._pubfile(name))

        return rsa
        
    def _makerequest(self, name, privkey, subject):
        """Create a Certificate Request (CSR).

					args:
						. name    : certificate request name
						. privkey : private key request is base on
						. subject : certificat information fields (CN, OU, O, L, ST, C, emailAddress)

					returns:
						. the request, and the associated public key
        """				
        # Create public key
        pubkey = EVP.PKey()
        pubkey.assign_rsa(privkey)

        # Create request
        req = X509.Request()
        #req.set_version(req.get_version())
        req.set_pubkey(pubkey)
        name = X509.X509_Name()
        name.CN           = subject.get('CN', '*')
        name.OU           = subject.get('OU', 'R&D Department')
        name.O            = subject.get('O' , 'Proformatique')
        name.L            = subject.get('L' , 'Puteaux')
        name.ST           = subject.get('ST', 'France')
        name.C            = subject.get('C' , 'FR')
        name.emailAddress = subject.get('emailAddress', 'xivo-users@lists.proformatique.com')
			
        req.set_subject_name(name)
        req.sign(pubkey, 'sha1')

        return req, pubkey

    def _makecert(self, request, (issuerCert, issuerKey), validity=365, extens={}):
        """Create a X509 certificate.

					Usually, a final certificate is signed by a CA.
					In this case, issuerCert and issuerKey are respectively the X509 CA
					certificate and the private key associated with.

					For a self-signed certificate, or a CA certificate, issuerCert is the request
					itself, and issuerKey the public key associated with.

					args:
						. request               : the request (CSR) for our certificate
						. issuerCert, issuerKey : certificate + key to sign CSR with (usually CA cert/key)
						. validity              : certificate validity duration (in days)
							certificate validity start from now until now+validity
						. extens                : certificat key/value extensions
							i.e: a CA certificate need 'basicConstraints: CA=TRUE' extension
							
					returns:
						the X509 certificate

					NOTE: certificate serial number MUST be unique.
        """				
        # Create x509 certificate
        cert = X509.X509()
        cert.set_version(2)
        cert.set_serial_number(random.randint(0,9999999999))

        t = ASN1.ASN1_UTCTIME()
        t.set_time(long(time.time()))
        cert.set_not_before(t)

        t = ASN1.ASN1_UTCTIME()
        t.set_time(long(time.time() + 60 * 60 * 24 * validity))
        cert.set_not_after(t)

        cert.set_pubkey(request.get_pubkey())
        cert.set_subject(request.get_subject())

        for k,v in extens.iteritems():
            exten = X509.new_extension(k,v)
            cert.add_ext(exten)

        cert.set_issuer(issuerCert.get_subject())
        cert.sign(issuerKey, 'sha1')

        return cert


    def createSSLCACertificate(self, args, options):
        """Create a CA certificate.

					args (* == required):
					  * name        (str)  : certificate name. MUST be unique
						. password    (str)  : CA password
								default = none
						. length      (int)  : private key size, in bits
								default = 1024
						. validity    (int)  : certificate validity (in days) from now
								default = 365

						== issuer/subject keys ==
						. CN           (str)  : CommonName                (default=*)
						. C            (str)  : Country                   (default=FR)
						. ST           (str)  : State                     (default=France)
						. L            (str)  : Location                  (default=Puteaux)
						. O            (str)  : Organization              (default=Proformatique)
						. OU           (str)  : OrganizationalUnit        (default=R&D)
						. emailAddress (str)  : ...             					(default=xivo-users@lists.proformatique.com)

					NOTE: we save certificate private key (ext .key), X509 certificate (ext .cert)
					and concanenation of both (ext .PEM) on disk in self.certsdir directory

				>>> createSSLCACertificate({
						'name'         : 'proformatique'
						'length'       : 1024,
						'validity'     : 365,
						'password'     : 'abcd',
						'CN'           : '*'
						'C'            : 'FR',
						'ST'           : 'France',
						'L'            : 'Puteaux',
						'O'            : 'Proformatique',
						'OU'           : 'R&D',
						'emailAddress' : 'xivo-users@lists.proformatique.com',
					}, {})
        """
        if 'name' not in args:
            raise HttpReqError(400, "missing 'name' option")
        elif os.path.exists(os.path.join(self.certsdir, args['name']+'.key')):
            raise HttpReqError(409, "a certificat with this name is already found")


        # Create private key
        pkey = self._makekey(args['name'], args.get('password',''), int(args.get('length',1024)))

        # Create request
        # pubkey != req.get_pubkey() !!!
        req, pubkey = self._makerequest(args['name'], pkey, args)

        # Create x509 certificate (autosigned)
        cert = self._makecert(req, (req, pubkey), args.get('validity', 365), {'basicConstraints': 'CA:TRUE'})

				# saving certificate
        cert.save(self._crtfile(args['name']))
				# make PEM as concatenation of key + x509 certificate
        pem = open(os.path.join(self.certsdir, args['name']+'.pem'), 'wb')
        for f in [os.path.join(self.certsdir, args['name']+ext) for ext in ('.key','.crt')]:
            shutil.copyfileobj(open(f, 'rb'), pem)
        pem.close()

        return True

    def createSSLCertificate(self, args, options):
        """
					args keys (* == required):
					  * name        (str)  : certificate name. MUST be unique
						. autosigned  (0|1)  : autosigned certificate
								default = 0
						. password    (str)  : CA password
								default = none
						. ca          (str)  : CA name (if autosigned == 0)
						. ca_password (str)  : if CA needs a password  (if not, you'll be throwed to hell!)
						. length      (int)  : private key size, in bits
								default = 1024
						. validity    (int)  : certificate validity (in days) from now
								default = 365
						. cipher      (str)  : 'des','des3',aes','idea'

						== issuer/subject keys ==
						. CN           (str)  : CommonName                (default=*)
						. C            (str)  : Country                   (default=FR)
						. ST           (str)  : State                     (default=France)
						. L            (str)  : Location                  (default=Puteaux)
						. O            (str)  : Organization              (default=Proformatique)
						. OU           (str)  : OrganizationalUnit        (default=R&D)
						. emailAddress (str)  : ...             					(default=xivo-users@lists.proformatique.com)

					NOTE: we save certificate private key (ext .key), X509 certificate (ext .cert)
					and concanenation of both (ext .PEM) on disk in self.certsdir directory

				>>> createSSLCertificate({
						'name'         : 'wiki'
						'length'       : 512,
						'validity'     : 15,
						'password'     : 'abcd',
						'CN'           : 'wiki.proformatique.com'
						'C'            : 'FR',
						'ST'           : 'France',
						'L'            : 'Puteaux',
						'O'            : 'Proformatique',
						'OU'           : 'R&D',
						'emailAddress' : 'gbour@proformatique.com',
					}, {})
        """
        if 'name' not in args:
            raise HttpReqError(400, "missing 'name' option")
        elif os.path.exists(os.path.join(self.certsdir, str(args['name'])+'.key')):
            raise HttpReqError(409, "a certificat with this name is already found")

        autosigned = int(args.get('autosigned',0))
        if autosigned == 0:
            if 'ca' not in args:
                raise HttpReqError(400, "missing 'ca' option")
            elif not os.path.exists(os.path.join(self.certsdir, str(args['ca'])+'.key')):
                raise HttpReqError(409, "CA certificate key not found")

            # loading CA private key
			    	#NOTE: RSA fail to read password (with "bad password read message") if we
    				#make "args.get()" IN _getpass()
            pwd = args.get('ca_password','')
            def _getpass(*args,**kwargs):
                return pwd

            try:
                _cakey = RSA.load_key(os.path.join(self.certsdir, args['ca']+'.key'), _getpass)
            except RSA.RSAError, e:
                raise HttpReqError(403, "invalid CA password")
            cakey = EVP.PKey()
            cakey.assign_rsa(_cakey)

            cacert = X509.load_cert(self._crtfile(args['ca']))
       
        cipher = CIPHERS.get(args.get('cipher'), DEFAULT_CIPHER)

        # Create private key
        pkey = self._makekey(args['name'], args.get('password',''),
						int(args.get('length',1024)), cipher)

        # Create request
        # pubkey != req.get_pubkey() !!!
        req, pubkey = self._makerequest(args['name'], pkey, args)
        if autosigned == 1:
            cacert = req; cakey = pubkey

        # Create x509 certificate / signed with CA key
        cert = self._makecert(req, (cacert, cakey), int(args.get('validity', 365)))
        cert.save(self._crtfile(args['name']))

				# make PEM as concatenation of key + x509 certificate
        pem = open(os.path.join(self.certsdir, args['name']+'.pem'), 'wb')
        for f in [os.path.join(self.certsdir, args['name']+ext) for ext in ('.key','.crt')]:
            shutil.copyfileobj(open(f, 'rb'), pem)
        pem.close()

        return True

    def deleteCertificate(self, args, options):
        """
        """
        if 'name' not in options:
            raise HttpReqError(400, "missing 'name' option")
        elif not os.path.exists(self._pemfile(options['name'])):
            raise HttpReqError(404, "a certificat with this name was not found")

        for fname in glob.glob(os.path.join(self.certsdir, options['name']+'.*')):
            os.remove(fname)

        return True

openssl = OpenSSL()
