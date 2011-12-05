# -*- coding: UTF-8 -*-
from xivo_agid import dialplan_variables


class Handler(object):

    def __init__(self, agi, cursor, args):
        self._agi = agi
        self._cursor = cursor
        self._args = args

    def _set_path(self, path_type, path_id):
        # schedule path
        path = self.agi.get_variable(dialplan_variables.PATH)
        if path is None or len(path) == 0:
            self.agi.set_variable(dialplan_variables.PATH, path_type)
            self.agi.set_variable(dialplan_variables.PATH_ID, path_id)

