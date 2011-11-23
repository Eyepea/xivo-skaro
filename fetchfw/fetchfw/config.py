# -*- coding: UTF-8 -*-

__license__ = """
    Copyright (C) 2010-2011  Avencall

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

from ConfigParser import RawConfigParser
from fetchfw.params import ConfigSpec


def _new_config_spec():
    cfg_spec = ConfigSpec()

    # [general] section definition
    cfg_spec.add_param('general.root_dir', default='/')
    cfg_spec.add_param('general.db_dir', default='/var/lib/pf-xivo-fetchfw')
    cfg_spec.add_param('general.cache_dir', default='/var/cache/pf-xivo-fetchfw')

    @cfg_spec.add_param_decorator('general.auth_sections', default=[])
    def _auth_sections_fun(raw_value):
        return raw_value.split()

    # [global_vars] section definition
    cfg_spec.add_section('global_vars')

    # [proxy] section definition
    cfg_spec.add_section('proxy')

    # dynamic [auth-section] definition (referenced by general.auth_sections)
    cfg_spec.add_dyn_param('auth-section', 'uri', default=ConfigSpec.MANDATORY)
    cfg_spec.add_dyn_param('auth-section', 'username', default=ConfigSpec.MANDATORY)
    cfg_spec.add_dyn_param('auth-section', 'password', default=ConfigSpec.MANDATORY)

    # unknown section hook for dynamic auth sections
    @cfg_spec.set_unknown_section_hook_decorator
    def _unknown_section_hook(config_dict, section_id, section_dict):
        if section_id in config_dict['general.auth_sections']:
            return 'auth-section'

    return cfg_spec

_CONFIG_SPEC = _new_config_spec()


def read_config(filename):
    config_parser = RawConfigParser()
    # case sensitive options (used for section 'global_vars')
    config_parser.optionxform = str
    with open(filename) as fobj:
        config_parser.readfp(fobj)
    return _CONFIG_SPEC.read_config(config_parser)
