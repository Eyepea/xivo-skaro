# -*- coding: UTF-8 -*-

"""Plugin for Zenitel IP stations using the 01.11.3.2 firmware.

"""

common_globals = {}
execfile_('common.py', common_globals)


class ZenitelPlugin(common_globals['BaseZenitelPlugin']):
    IS_PLUGIN = True
