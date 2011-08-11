# -*- coding: UTF-8 -*-

__license__ = """
    Copyright (C) 2011  Proformatique <technique@proformatique.com>

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

# TODO wrap some exceptions at client level, especially the one that are
#      easy to process
# XXX Configs.update and Devices.update are more of a replace operation than
#     an update operation, we might want to change the name, although we have
#     use the word update everywhere else (server part)

from copy import deepcopy
from time import sleep
from sys import stdout
from itertools import chain
from provd.operation import parse_oip, OIP_SUCCESS, OIP_FAIL, OIP_WAITING,\
    OIP_PROGRESS, OperationInProgress
from provd.persist.common import ID_KEY
from provd.rest.client.client import new_provisioning_client


class _Options(object):
    # XXX eventually some values could be properties and we could be aware
    #     when some values change if it's useful...
    def __init__(self):
        self.search_description = True
        self.search_case_sensitive = False
        self.op_progress = True
        self.op_async = False
        self.oip_update_interval = 1.0

OPTIONS = _Options()


_FMT_STATE_MAP = {
    OIP_WAITING: 'waiting...',
    OIP_PROGRESS: 'in progress...',
    OIP_FAIL: 'failed.',
    OIP_SUCCESS: 'done.'
}

def _format_oip(oip):
    # format the oip
    dict_ = {}
    if oip.label:
        dict_['label'] = "'%s'" % oip.label
    else:
        dict_['label'] = 'operation'
    dict_['state'] = _FMT_STATE_MAP[oip.state]
    if oip.current is not None:
        if oip.end:
            dict_['xy'] = '%s/%s' % (oip.current, oip.end)
        else:
            dict_['xy'] = oip.current
    else:
        dict_['xy'] = ''
    return '%(label)s %(state)s %(xy)s' % dict_


def _format_oip_line(oip, tree_pos, sw=4):
    # format oip on a line, i.e. format the oip with correct leading indent.
    # Note: tree_pos is only used to compute indent
    indent = ' ' * (sw * len(tree_pos))
    fmted_oip = _format_oip(oip)
    return indent + fmted_oip


def _build_write_table(oip):
    # a write table is a list where item are position specification
    # - a position specification is a tuple (tree position, completed)
    #   - a tree position is a tuple that is used to reach the oip in an oip tree
    #   - completed is true when the item represent an completed operation (i.e.
    #     an operation in state fail or success), else false
    def aux(cur_oip, cur_pos):
        sub_table = []
        for pos_suffix, oip in enumerate(cur_oip.sub_oips):
            pos = cur_pos + (pos_suffix,)
            sub_table.extend(aux(oip, pos))
        return list(chain([(cur_pos, False)], sub_table, [(cur_pos, True)]) )
    return aux(oip, ())


def _retrieve_oip(top_oip, tree_pos):
    # return the oip at tree position tree_pos
    oip = top_oip
    for pos in tree_pos:
        oip = oip.sub_oips[pos]
    return oip


def _write_oip_info(top_oip, init_pos_spec, cur_pos_spec, fobj):
    # This function write the the line between init_pos_spec and cur_pos_spec.
    # If they are the same, rewrite the line at init_pos_spec
    # 1. create a flat list of operation to visit
    write_table = _build_write_table(top_oip)
    # 2. find the one will visit in this call
    init_idx = write_table.index(init_pos_spec)
    cur_idx = write_table.index(cur_pos_spec)
    # 3. write the lines...
    pos_specs = set(write_table[init_idx:cur_idx+1])
    for idx in xrange(init_idx, cur_idx + 1):
        tree_pos, completed = write_table[idx]
        oip = _retrieve_oip(top_oip, tree_pos)
        if not completed and (tree_pos, True) in pos_specs:
            if idx == init_idx and idx != 0:
                # just skip it
                fobj.write('\n')
                continue
            else:
                # we need to rewrite the oip
                oip = OperationInProgress(oip.label, OIP_PROGRESS)
        line = _format_oip_line(oip, tree_pos)
        fobj.write('\r' + line)
        if idx != cur_idx:
            fobj.write('\n')
        fobj.flush()


def _find_active_oip(top_oip):
    # return the position specification of the active oip
    def aux(cur_oip, cur_tree_pos):
        if cur_oip.state in [OIP_SUCCESS, OIP_FAIL]:
            return (cur_tree_pos, True)
        for pos_suffix, oip in enumerate(cur_oip.sub_oips):
            if oip.state == OIP_PROGRESS:
                return aux(oip, cur_tree_pos + (pos_suffix,))
        else:
            # oip.state is either waiting or progress
            return (cur_tree_pos, False)
    return aux(top_oip, ())


def _display_operation_in_progress(client_oip):
    init_pos_spec = ((), False)
    while True:
        top_oip = parse_oip(client_oip.status())
        cur_pos_spec = _find_active_oip(top_oip)
        _write_oip_info(top_oip, init_pos_spec, cur_pos_spec, stdout)
        if top_oip.state in [OIP_SUCCESS, OIP_FAIL]:
            # operation completed
            assert cur_pos_spec == ((), True)
            break
        else:
            init_pos_spec = cur_pos_spec
            sleep(OPTIONS.oip_update_interval)
    print


def _nodisplay_operation_in_progress(client_oip):
    while True:
        top_oip = parse_oip(client_oip.status())
        if top_oip.state in [OIP_SUCCESS, OIP_FAIL]:
            break
        else:
            sleep(OPTIONS.oip_update_interval)
    print _format_oip_line(top_oip, ())


def _search_in_pkgs_gen(pkgs, search):
    # define search package predicate
    if OPTIONS.search_description:
        def search_pkg_pred(pkg_idpkg_name, pkg):
            if search_pred(pkg_id):
                return True
            else:
                if u'description' in pkg:
                    return search_pred(pkg[u'description'])
            return False 
    else:
        def search_pkg_pred(pkg_id, pkg):
            return search_pred(pkg_id)
    # define search predicate
    if OPTIONS.search_case_sensitive:
        def search_pred(value):
            return search in value
    else:
        search = search.lower()
        def search_pred(value):
            return search in value.lower()
    for pkg_id, pkg in pkgs.iteritems():
        if search_pkg_pred(pkg_id, pkg):
            yield pkg_id, pkg


def _search_in_pkgs(pkgs, search):
    # return only the pkgs that match the search
    if search is None:
        return pkgs
    else:
        return dict(_search_in_pkgs_gen(pkgs, search))


def _get_id(id_or_dict):
    if isinstance(id_or_dict, basestring):
        return id_or_dict
    else:
        return id_or_dict[ID_KEY]


class ProvisioningClient(object):
    def __init__(self, prov_client):
        self._prov_client = prov_client
    
    def configs(self):
        return Configs(self._prov_client.config_manager())
    
    def devices(self):
        return Devices(self._prov_client.device_manager())
    
    def plugins(self):
        return Plugins(self._prov_client.plugin_manager())
    
    def parameters(self):
        return Parameters(self._prov_client.configure_service())
    
    def test_connectivity(self):
        self._prov_client.test_connectivity()


def _rec_update_dict(base_dict, overlay_dict):
    # update a base dictionary from another dictionary
    for k, v in overlay_dict.iteritems():
        if isinstance(v, dict):
            old_v = base_dict.get(k)
            if isinstance(old_v, dict):
                _rec_update_dict(old_v, v)
            else:
                base_dict[k] = {}
                _rec_update_dict(base_dict[k], v)
        else:
            base_dict[k] = v


def _expand_dotted_dict(dotted_dict):
    # return a new dictionary which is the same as dotted dict except that it
    # is 'expanded'
    # Note that every key of the dictionary must be string and every keys of
    # dictionaries must also be string
    res = {}
    for raw_k, raw_v in dotted_dict.iteritems():
        if isinstance(raw_v, dict):
            v = _expand_dotted_dict(raw_v)
        else:
            v = raw_v
        pre, sep, post = raw_k.partition('.')
        if not sep:
            k = raw_k
        else:
            k = pre
            v = _expand_dotted_dict({post: v})
        res[k] = v
    return res


class Configs(object):
    def __init__(self, cfg_mgr):
        self._cfg_mgr = cfg_mgr
    
    def add(self, dotted_config):
        config = _expand_dotted_dict(dotted_config)
        return self._cfg_mgr.add(config)
    
    def get(self, id_or_config):
        id = _get_id(id_or_config)
        return self._cfg_mgr.get(id)
    
    def get_raw(self, id_or_config):
        id = _get_id(id_or_config)
        return self._cfg_mgr.get_raw(id)
    
    def update(self, dotted_config):
        config = _expand_dotted_dict(dotted_config)
        self._cfg_mgr.update(config)
    
    def remove(self, id_or_config):
        id = _get_id(id_or_config)
        self._cfg_mgr.remove(id)
    
    def remove_all(self):
        for config in self._cfg_mgr.find({}):
            config_id = config[ID_KEY]
            print 'Removing config %s' % config_id
            self._cfg_mgr.remove(config_id)
    
    def autocreate(self):
        return self._cfg_mgr.autocreate()
    
    def clone(self, id_or_config, new_id=None):
        old_id = _get_id(id_or_config)
        config = self._cfg_mgr.get(old_id)
        if new_id is not None:
            config[ID_KEY] = new_id
        return self._cfg_mgr.add(config)
    
    def find(self, *args, **kwargs):
        return self._cfg_mgr.find(*args, **kwargs)
    
    def __getitem__(self, name):
        return Config(name, self._cfg_mgr)
    
    def count(self):
        return len(self._cfg_mgr.find(fields=[ID_KEY]))


class Config(object):
    def __init__(self, id, cfg_mgr):
        self._id = id
        self._cfg_mgr = cfg_mgr
    
    @property
    def id(self):
        return self._id
    
    def get(self):
        return self._cfg_mgr.get(self._id)
    
    def get_raw(self):
        return self._cfg_mgr.get_raw(self._id)
    
    def set_config(self, dotted_values):
        values = _expand_dotted_dict(dotted_values)
        old_config = self._cfg_mgr.get(self._id)
        new_config = deepcopy(old_config)
        _rec_update_dict(new_config[u'raw_config'], values)
        if new_config != old_config:
            self._cfg_mgr.update(new_config)
        return self
    
    def unset_config(self, *raw_values):
        old_config = self._cfg_mgr.get(self._id)
        new_config = deepcopy(old_config)
        for raw_value in raw_values:
            keys = raw_value.split('.')
            cur_dict = new_config[u'raw_config']
            for key in keys[:-1]:
                if key in cur_dict and isinstance(cur_dict[key], dict):
                    cur_dict = cur_dict[key]
                else:
                    break
            else:
                key = keys[-1]
                if key in cur_dict:
                    del cur_dict[key]
        if old_config != new_config:
            self._cfg_mgr.update(new_config)
        return self
    
    def set_parents(self, *parents):
        config = self._cfg_mgr.get(self._id)
        config[u'parent_ids'] = list(parents)
        self._cfg_mgr.update(config)


class Devices(object):
    def __init__(self, dev_mgr):
        self._dev_mgr = dev_mgr

    def add(self, device):
        return self._dev_mgr.add(device)
    
    def get(self, id_or_device):
        # return a device as a dictionary
        # see __getitem__ to retrieve it as an object
        id = _get_id(id_or_device)
        return self._dev_mgr.get(id)
    
    def update(self, device):
        self._dev_mgr.update(device)
    
    def remove(self, id_or_device):
        id = _get_id(id_or_device)
        self._dev_mgr.remove(id)
    
    def remove_all(self):
        for device in self._dev_mgr.find({}):
            device_id = device[ID_KEY]
            print 'Removing device %s' % device_id
            self._dev_mgr.remove(device_id)
    
    def reconfigure(self, id_or_device):
        id = _get_id(id_or_device)
        self._dev_mgr.reconfigure(id)
    
    def synchronize(self, id_or_device):
        id = _get_id(id_or_device)
        client_oip = self._dev_mgr.synchronize(id)
        try:
            _display_operation_in_progress(client_oip)
        finally:
            client_oip.delete()
    
    def find(self, *args, **kwargs):
        return self._dev_mgr.find(*args, **kwargs)
    
    def __getitem__(self, name):
        return Device(name, self._dev_mgr)
    
    def count(self):
        return len(self._dev_mgr.find(fields=[ID_KEY]))


class Device(object):
    # handy way to do simple modification to a device
    def __init__(self, id, dev_mgr):
        self._id = id
        self._dev_mgr = dev_mgr
    
    @property
    def id(self):
        return self._id
    
    def get(self):
        return self._dev_mgr.get(self._id)
    
    def set(self, values):
        old_device = self._dev_mgr.get(self._id)
        new_device = deepcopy(old_device)
        for k, v in values.iteritems():
            new_device[k] = v
        if new_device != old_device:
            self._dev_mgr.update(new_device)
        return self
    
    def unset(self, *values):
        old_device = self._dev_mgr.get(self._id)
        new_device = deepcopy(old_device)
        for k in values:
            if k in old_device:
                del new_device[k]
        if new_device != old_device:
            self._dev_mgr.update(new_device)
        return self
    
    def reconfigure(self):
        self._dev_mgr.reconfigure(self._id)
        return self
    
    def synchronize(self):
        client_oip = self._dev_mgr.synchronize(self._id)
        try:
            _display_operation_in_progress(client_oip)
        finally:
            client_oip.delete()


class Plugins(object):
    def __init__(self, pg_mgr):
        self._pg_mgr = pg_mgr
    
    def install(self, id):
        install_srv = self._pg_mgr.install_service()
        client_oip = install_srv.install(id)
        try:
            _display_operation_in_progress(client_oip)
        finally:
            client_oip.delete()
    
    def upgrade(self, id):
        install_srv = self._pg_mgr.install_service()
        client_oip = install_srv.upgrade(id)
        _display_operation_in_progress(client_oip)
        client_oip.delete()
    
    def uninstall(self, id):
        install_srv = self._pg_mgr.install_service()
        install_srv.uninstall(id)
    
    def uninstall_all(self):
        install_srv = self._pg_mgr.install_service()
        pg_ids = sorted(install_srv.installed())
        for pg_id in pg_ids:
            print 'Uninstalling plugin %s' % pg_id
            install_srv.uninstall(pg_id)
    
    def update(self):
        install_srv = self._pg_mgr.install_service()
        client_oip = install_srv.update()
        if OPTIONS.op_async:
            return client_oip
        else:
            try:
                if OPTIONS.op_progress:
                    _display_operation_in_progress(client_oip)
                else:
                    _nodisplay_operation_in_progress(client_oip)
            finally:
                client_oip.delete()
    
    def installed(self, search=None):
        install_srv = self._pg_mgr.install_service()
        return _search_in_pkgs(install_srv.installed(), search)
    
    def installable(self, search=None):
        install_srv = self._pg_mgr.install_service()
        return _search_in_pkgs(install_srv.installable(), search)
    
    def __getitem__(self, id):
        # return the plugin with id id
        return Plugin(self._pg_mgr.plugin(id))
    
    def count_installed(self):
        install_srv = self._pg_mgr.install_service()
        return len(install_srv.installed())


class Parameters(object):
    def __init__(self, config_srv):
        self._config_srv = config_srv
    
    def infos(self):
        return self._config_srv.infos()
    
    def get(self, key):
        return self._config_srv.get(key)
    
    def set(self, key, value):
        self._config_srv.set(key, value)
    
    def unset(self, key):
        # equivalent to set(key, None)
        self._config_srv.set(key, None)


class Plugin(object):
    def __init__(self, client_plugin):
        self._client_plugin = client_plugin
    
    def install(self, id):
        install_srv = self._client_plugin.install_service()
        client_oip = install_srv.install(id)
        try:
            _display_operation_in_progress(client_oip)
        finally:
            client_oip.delete()
    
    def install_all(self):
        """Install all the packages available from this plugin."""
        install_srv = self._client_plugin.install_service()
        pkg_ids = sorted(install_srv.installable())
        for pkg_id in pkg_ids:
            print 'Installing package %s' % pkg_id
            client_oip = install_srv.install(pkg_id)
            try:
                _display_operation_in_progress(client_oip)
            finally:
                client_oip.delete()
            print
    
    def upgrade(self, id):
        install_srv = self._client_plugin.install_service()
        client_oip = install_srv.upgrade(id)
        try:
            _display_operation_in_progress(client_oip)
        finally:
            client_oip.delete()
    
    def uninstall(self, id):
        install_srv = self._client_plugin.install_service()
        install_srv.uninstall(id)
    
    def uninstall_all(self):
        install_srv = self._client_plugin.install_service()
        pkg_ids = sorted(install_srv.installed())
        for pkg_id in pkg_ids:
            print 'Uninstalling package %s' % pkg_id
            install_srv.uninstall(pkg_id)
    
    def update(self):
        install_srv = self._client_plugin.install_service()
        client_oip = install_srv.update()
        try:
            _display_operation_in_progress(client_oip)
        finally:
            client_oip.delete()
    
    def installed(self, search=None):
        install_srv = self._client_plugin.install_service() 
        return _search_in_pkgs(install_srv.installed(), search)
    
    def installable(self, search=None):
        install_srv = self._client_plugin.install_service()
        return _search_in_pkgs(install_srv.installable(), search)
    
    def parameters(self):
        return Parameters(self._client_plugin.configure_service())


def new_pycli_provisioning_client(server_uri, credentials):
    prov_client = new_provisioning_client(server_uri, credentials)
    return ProvisioningClient(prov_client)
