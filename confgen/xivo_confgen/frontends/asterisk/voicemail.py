# -*- coding: UTF-8 -*-

__license__ = """
    Copyright (C) 2011 Proformatique

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""

from collections import defaultdict
from xivo_confgen.frontends.asterisk.util import format_ast_section, \
    format_ast_option, format_ast_object_option, format_none_as_empty


class VoicemailConf(object):
    def __init__(self, voicemail, voicemails):
        self._voicemail = voicemail
        self._voicemails = voicemails

    def generate(self, output):
        self._gen_general_section(output)
        print >> output
        self._gen_zonemessages_section(output)
        print >> output
        self._gen_context_sections(output)

    def _gen_general_section(self, output):
        print >> output, u'[general]'
        for item in self._voicemail:
            if item['category'] == u'general':
                opt_name = item['var_name']
                if opt_name == u'emailbody':
                    opt_val = self._format_emailbody(item['var_val'])
                else:
                    opt_val = item['var_val']
                print >> output, format_ast_option(opt_name, opt_val)

    def _format_emailbody(self, emailbody):
        return emailbody.replace(u'\n', u'\\n')

    def _gen_zonemessages_section(self, output):
        print >> output, u'[zonemessages]'
        for item in self._voicemail:
            if item['category'] == u'zonemessages':
                print >> output, format_ast_option(item['var_name'], item['var_val'])

    def _gen_context_sections(self, output):
        mailbox_by_context = defaultdict(list)
        for mailbox in self._voicemails:
            mailbox_by_context[mailbox['context']].append(mailbox)

        for context, mailboxes in mailbox_by_context.iteritems():
            self._gen_context_section(output, context, mailboxes)
            print >> output

    def _gen_context_section(self, output, context, mailboxes):
        print >> output, format_ast_section(context)
        for mailbox in mailboxes:
            opt_name = mailbox['mailbox']
            opt_value = self._format_mailbox(mailbox)
            print >> output, format_ast_object_option(opt_name, opt_value)

    def _format_mailbox(self, mailbox):
        mailbox_options = self._format_mailbox_options(mailbox)
        return u'%s,%s,%s,%s,%s' % (mailbox['password'],
                                    mailbox['fullname'],
                                    format_none_as_empty(mailbox['email']),
                                    format_none_as_empty(mailbox['pager']),
                                    mailbox_options)

    _MAILBOX_NOT_OPTIONS = [u'uniqueid', u'context', u'mailbox', u'password',
                            u'fullname', u'email', u'pager', u'commented']

    def _format_mailbox_options(self, mailbox):
        return u'|'.join(u'%s=%s' % (name, value)
                         for name, value in mailbox.iteritems()
                         if value is not None and name not in self._MAILBOX_NOT_OPTIONS)

    @classmethod
    def new_from_backend(cls, backend):
        voicemail = backend.voicemail.all(commented=False)
        voicemails = backend.voicemails.all(commented=False)
        return cls(voicemail, voicemails)
