# -*- coding: UTF-8 -*-

import os
import StringIO
import unittest
import mock
from xivo_confgen.frontends.asterisk.voicemail import VoicemailConf
from xivo_confgen.frontends.asterisk.tests.util import parse_ast_config


class TestVoicemailConf(unittest.TestCase):
    def setUp(self):
        self._output = StringIO.StringIO()

    def _parse_ast_cfg(self):
        self._output.seek(os.SEEK_SET)
        return parse_ast_config(self._output)

    def test_empty_sections(self):
        voicemail_conf = VoicemailConf([], [])
        voicemail_conf.generate(self._output)

        result = self._parse_ast_cfg()
        expected = {u'general': [],
                    u'zonemessages': []}
        self.assertEqual(expected, result)

    def test_one_element_general_section(self):
        voicemail = [{'category': u'general',
                      'var_name': u'foo',
                      'var_val': u'bar'}]
        voicemail_conf = VoicemailConf(voicemail, [])
        voicemail_conf.generate(self._output)

        result = self._parse_ast_cfg()
        expected = {u'general': [u'foo = bar'],
                    u'zonemessages': []}
        self.assertEqual(expected, result)

    def test_one_element_zonemessages_section(self):
        voicemail = [{'category': u'zonemessages',
                      'var_name': u'foo',
                      'var_val': u'bar'}]
        voicemail_conf = VoicemailConf(voicemail, [])
        voicemail_conf.generate(self._output)

        result = self._parse_ast_cfg()
        expected = {u'general': [],
                    u'zonemessages': [u'foo = bar']}
        self.assertEqual(expected, result)

    def test_escape_general_emailbody_option(self):
        voicemail = [{'category': u'general',
                      'var_name': u'emailbody',
                      'var_val': u'foo\nbar'}]
        voicemail_conf = VoicemailConf(voicemail, [])
        voicemail_conf.generate(self._output)

        result = self._parse_ast_cfg()
        expected = {u'general': [u'emailbody = foo\\nbar'],
                    u'zonemessages': []}
        self.assertEqual(expected, result)

    def test_one_mailbox(self):
        voicemails = [{'context': u'default',
                       'mailbox': u'm1',
                       'password': u'p1',
                       'fullname': u'Foo Bar',
                       'email': u'foo@example.org',
                       'pager': u''}]
        voicemail_conf = VoicemailConf([], voicemails)
        voicemail_conf.generate(self._output)

        result = self._parse_ast_cfg()
        expected = {u'general': [],
                    u'zonemessages': [],
                    u'default': [u'm1 => p1,Foo Bar,foo@example.org,,']}
        self.assertEqual(expected, result)

    def test_two_mailboxes_same_context(self):
        voicemails = [{'context': u'ctx1',
                       'mailbox': u'm1',
                       'password': u'',
                       'fullname': u'f1',
                       'email': u'',
                       'pager': u''},
                      {'context': u'ctx1',
                       'mailbox': u'm2',
                       'password': u'',
                       'fullname': u'f2',
                       'email': u'',
                       'pager': u''}]
        voicemail_conf = VoicemailConf([], voicemails)
        voicemail_conf.generate(self._output)

        result = self._parse_ast_cfg()
        expected = {u'general': [],
                    u'zonemessages': [],
                    u'ctx1': [u'm1 => ,f1,,,',
                              u'm2 => ,f2,,,']}
        self.assertEqual(expected, result)

    def test_two_mailboxes_different_context(self):
        voicemails = [{'context': u'ctx1',
                       'mailbox': u'm1',
                       'password': u'',
                       'fullname': u'f1',
                       'email': u'',
                       'pager': u''},
                      {'context': u'ctx2',
                       'mailbox': u'm2',
                       'password': u'',
                       'fullname': u'f2',
                       'email': u'',
                       'pager': u''},
                      ]
        voicemail_conf = VoicemailConf([], voicemails)
        voicemail_conf.generate(self._output)

        result = self._parse_ast_cfg()
        expected = {u'general': [],
                    u'zonemessages': [],
                    u'ctx1': [u'm1 => ,f1,,,'],
                    u'ctx2': [u'm2 => ,f2,,,']}
        self.assertEqual(expected, result)

    def test_new_from_backend(self):
        backend = mock.Mock()
        VoicemailConf.new_from_backend(backend)

        backend.voicemail.all.assert_called_once_with(commented=False)
        backend.voicemails.all.assert_called_once_with(commented=False)
