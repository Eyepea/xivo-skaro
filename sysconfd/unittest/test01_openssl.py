#!/usr/bin/env python
# -*- coding: utf8 -*-
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011  Avencall

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
import unittest, cjson, pprint
import sysconfd_client

class TestOpenSSL(unittest.TestCase):
	def setUp(self):
		self.client = sysconfd_client.SysconfdClient()

	"""
	@classmethod
	def tearDownClass(self):
		# do cleanup
		print 'CLEANUP...'
		(resp, data) = self.client.request('GET', '/openssl_listcertificates', {})
		for cert in cjson.decode(data):
			self.client.request('GET',	'/openssl_deletecertificate', {'name':cert['name']})
	"""

	def test_01_createCA(self):
		# no name
		(resp, data) = self.client.request('POST', '/openssl_createcacertificate', {})
		self.assertEqual(resp.status, 400)

		# with default values
		(resp, data) = self.client.request('POST', '/openssl_createcacertificate',
				{'name': 'catest1'})
		self.assertEqual(resp.status, 200)

		# already existing certificate
		(resp, data) = self.client.request('POST', '/openssl_createcacertificate',
				{'name': 'catest1'})
		self.assertEqual(resp.status, 409)

		# with custom values
		(resp, data) = self.client.request('POST', '/openssl_createcacertificate',
				{
					'name'     : 'catest2',
					'length'   : 512,
					'validity' : 12,
					'CN'       : 'proformatique.com',
					'Email'    : 'g.bour@proformatique.com',
				})
		self.assertEqual(resp.status, 200)

		# with a password
		(resp, data) = self.client.request('POST', '/openssl_createcacertificate',
				{
					'name'     : 'catest3',
					'password' : 'a*45$l3',
					'length'   : 512,
					'validity' : 12,
					'CN'       : 'proformatique.com',
					'Email'    : 'g.bour@proformatique.com',
				})
		self.assertEqual(resp.status, 200)

	def test_10_createClientCert(self):
		# autosigned certificate
		(resp, data) = self.client.request('POST', '/openssl_createcertificate',
				{
					'name'      : 'usercert1',
					'autosigned': 1,
					'CN'        : 'wiki.xivo.com',
					'length'    : 432,
				})
		self.assertEqual(resp.status, 200)
		
		# signed with passwordless CA
		(resp, data) = self.client.request('POST', '/openssl_createcertificate',
				{
					'ca'        : 'catest2',
					'name'      : 'usercert2',
					'CN'        : '*',
				})
		self.assertEqual(resp.status, 200)

		# signed with CA (password set) - no password sended
		(resp, data) = self.client.request('POST', '/openssl_createcertificate',
				{
					'ca'  : 'catest3',
					'name': 'usercert3'
				})
		self.assertEqual(resp.status, 403)

		# signed with CA (password set) - password sended
		(resp, data) = self.client.request('POST', '/openssl_createcertificate',
				{
					'ca'         : 'catest3',
					'name'       : 'usercert4',
					'ca_password': 'a*45$l3',
					'emailAddress': 'gbour@proformatique.com',
				})
		self.assertEqual(resp.status, 200)

		# self-signed certificate with password
		(resp, data) = self.client.request('POST', '/openssl_createcertificate',
				{
					'name'        : 'usercert5',
					'autosigned'  : 1,
					'CN'          : 'blog.xivo.fr',
					'password'    : 'plop',
				})
		self.assertEqual(resp.status, 200)

		# None value as CA name
		(resp, data) = self.client.request('POST', '/openssl_createcertificate',
				{
					'name'     : 'fail1',
					'length'   : 512,
					'ca'       : None,
				})
		self.assertEqual(resp.status, 409)

		# Certificate with des3 key cipher
		(resp, data) = self.client.request('POST', '/openssl_createcertificate',
				{
					'name'      : 'usercert6',
					'autosigned': 1,
					'password'  : 'fooo',
					'cipher'    : 'des3'
				})
		self.assertEqual(resp.status, 200)


	def test_20_listcerts(self):
		"""
			Example of resulting data:

			[
				 # private key
				 {'filename': 'usercert6.key', 'name': 'usercert6', 'types': ['privkey']},
				 # public key
				 {'filename': 'usercert2.pub', 'name': 'usercert2', 'types': ['pubkey']},
				 # autosigned certificate concatenated with private key
				 {'CA': False,
				  'autosigned': True,
				  'filename': 'usercert1.pem',
				  'fingerprint': 'md5:D23EE328AB37F7A5475FCCED32C3D92C',
				  'length': 432,
				  'name': 'usercert1',
				  'types': ['certificate', 'privkey'],
				  'validity-end': '2012/06/20 12:53:50 UTC'},
				 {'CA': False,
				  'autosigned': True,
				  'filename': 'usercert1.crt',
				  'fingerprint': 'md5:D23EE328AB37F7A5475FCCED32C3D92C',
				  'length': 432,
				  'name': 'usercert1',
				  'types': ['certificate'],
				  'validity-end': '2012/06/20 12:53:50 UTC'},
				 # CA certificate
				 {'CA': True,
				  'autosigned': True,
				  'filename': 'catest1.pem',
				  'fingerprint': 'md5:D652B931E03FB10E097C05BEBBDB6805',
				  'length': 1024,
				  'name': 'catest1',
				  'types': ['certificate'],
				  'validity-end': '2012/06/20 12:53:50 UTC'},
         # certificate signed with a CA
				 {'CA': False,
				  'autosigned': False,
				  'filename': 'usercert4.crt',
				  'fingerprint': 'md5:5FBE945BA50E87716A2647143FB2C392',
				  'length': 1024,
				  'name': 'usercert4',
				  'types': ['certificate'],
				  'validity-end': '2012/06/20 12:53:51 UTC'}
			]
		"""
		(resp, data) = self.client.request('GET', '/openssl_listcertificates', {})
		self.assertEqual(resp.status, 200)

		try:
			data = cjson.decode(data)
		except Exception:
			fail('cannot decode json data')

		# do we have our 32 certificates 
		# (each certificate creation create 4 files (cert, privkey, pubkey, cert+privkey)
		self.assertEqual(len(data), 32)
		# whose 3 are CA certificates
		self.assertEqual(len(filter(lambda c: c.get('CA',0) == 1, data)), 6)


	def test_30_getinfos(self):
		# CA
		(resp, data) = self.client.request('GET',	'/openssl_certificateinfos',
			{'name': 'catest1.crt'})
		self.assertEqual(resp.status, 200)

		try:
			data = cjson.decode(data)
		except Exception:
			fail('cannot decode cjson data')

		self.assertEqual(data['CA']    , 1)
		self.assertEqual(data['length'], 1024)

		# self-signed certificate
		(resp, data) = self.client.request('GET',	'/openssl_certificateinfos',
			{'name': 'usercert1.pem'})
		self.assertEqual(resp.status, 200)

		try:
			data = cjson.decode(data)
		except Exception:
			fail('cannot decode cjson data')

		for k in ('sn','CA','length','fingerprint','validity-start','validity-end','subject','issuer'):
			self.assertTrue(k in data)

		for k in ('C','CN','L','O','OU','ST','emailAddress'):
			self.assertTrue(k in data['subject'])
			self.assertTrue(k in data['issuer'])

		self.assertEqual(data['CA']    , 0)
		self.assertEqual(data['length'], 432)
		self.assertEqual(data['subject']['CN'], 'wiki.xivo.com')

		# CA-signed certificat
		(resp, data) = self.client.request('GET',	'/openssl_certificateinfos',
			{'name': 'usercert4.crt'})
		self.assertEqual(resp.status, 200)

		try:
			data = cjson.decode(data)
		except Exception:
			fail('cannot decode cjson data')

		self.assertEqual(data['CA']    , 0)
		self.assertNotEqual(data['subject']['emailAddress'], data['issuer']['emailAddress'])


		# limit cases
		# 	. file do not exists
		(resp, data) = self.client.request('GET',	'/openssl_certificateinfos',
			{'name': 'foo'})
		self.assertEqual(resp.status, 404)


	def test_31_exports(self):
		# public key
		(resp, data) = self.client.request('GET', '/openssl_export', {'name': 'usercert1.pub'})
		self.assertEqual(resp.status, 200)

		try:
			data = cjson.decode(data)
		except Exception:
			fail('cannot decode cjson data')

		self.assertTrue(data.startswith('-----BEGIN PUBLIC KEY-----'))

		# private key
		(resp, data) = self.client.request('GET', '/openssl_export', {'name': 'usercert1.key'})
		self.assertEqual(resp.status, 200)

		try:
			data = cjson.decode(data)
		except Exception:
			fail('cannot decode cjson data')

		self.assertFalse(data.startswith('-----BEGIN PUBLIC KEY-----'))

		# limit cases
		#		. no name
		(resp, data) = self.client.request('GET', '/openssl_export', {})
		self.assertEqual(resp.status, 400)

		# 	. file not found
		(resp, data) = self.client.request('GET', '/openssl_export', {'name': 'foo.bar'})
		self.assertEqual(resp.status, 404)


	def test_40_delete(self):
		(resp, data) = self.client.request('GET',	'/openssl_deletecertificate', {'name':'usercert4.pub'})
		self.assertEqual(resp.status, 200)

		# delete twice the same certificate
		(resp, data) = self.client.request('GET',	'/openssl_deletecertificate', {'name':'usercert4.pub'})
		self.assertEqual(resp.status, 404)
	
		# we must now only have 31 files	
		(resp, data) = self.client.request('GET', '/openssl_listcertificates', {})
		self.assertEqual(resp.status, 200)

		try:
			data = cjson.decode(data)
		except Exception:
			fail('cannot decode json data')

		self.assertEqual(len(data), 31)


	def test_50_imports(self):
		with open('./cert2.pub') as f:
			pubkey = f.read()

		(resp, data) = self.client.request('POST', '/openssl_import', 
				{'name': 'import1', 'content': pubkey})
		self.assertEqual(resp.status, 200)

		with open('./cert1.pem') as f:
			cert = f.read()

		(resp, data) = self.client.request('POST', '/openssl_import', 
			{'name': 'import2', 'content': cert})
		self.assertEqual(resp.status, 200)

		## limit cases
		#    . no name
		(resp, data) = self.client.request('POST', '/openssl_import', {'content': cert})
		self.assertEqual(resp.status, 400)

		#    . no content
		(resp, data) = self.client.request('POST', '/openssl_import', {'name': 'foo'})
		self.assertEqual(resp.status, 400)

		#    . file already found
		(resp, data) = self.client.request('POST', '/openssl_import', 
				{'name': 'import2', 'content': cert})
		self.assertEqual(resp.status, 500)

		#		. content is not a valid SSL certificate or key
		with open('./test01_openssl.py') as f:
			content = f.read()

		(resp, data) = self.client.request('POST', '/openssl_import', 
				{'name': 'foo', 'content': content})
		self.assertEqual(resp.status, 500)


	def test_99_cleanup(self):
		#NOTE: this last test is only to do cleanup
		(resp, data) = self.client.request('GET', '/openssl_listcertificates', {})
		for cert in cjson.decode(data):
			self.client.request('GET',	'/openssl_deletecertificate', {'name':cert['filename']})

if __name__ == '__main__':
	unittest.main()
