# -*- coding: UTF-8 -*-

import os
import shutil
import tempfile
import unittest
from xivo_sysconf.modules.asterisk import Asterisk


class TestAsterisk(unittest.TestCase):
    def setUp(self):
        self._base_voicemail_path = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._base_voicemail_path)

    def _make_voicemail_path(self, context, voicemail_id):
        voicemail_path = os.path.join(self._base_voicemail_path, context,
                                      voicemail_id)
        os.makedirs(voicemail_path)
        return voicemail_path

    def test_delete_voicemail_deletes_voicemail_path(self):
        context = 'foo'
        voicemail_id = '100'
        voicemail_path = self._make_voicemail_path(context, voicemail_id)

        asterisk_obj = Asterisk(self._base_voicemail_path)
        asterisk_obj.delete_voicemail(None, {'context': context, 'name': voicemail_id})

        self.assertFalse(os.path.exists(voicemail_path))
