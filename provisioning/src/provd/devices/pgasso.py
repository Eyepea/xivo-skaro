# -*- coding: UTF-8 -*-

"""Automatic plugin association."""

__version__ = "$Revision$ $Date$"
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

import logging
from collections import defaultdict
from operator import itemgetter
from provd.devices.ident import IDeviceUpdater
from twisted.internet import defer
from zope.interface import Interface, implements

logger = logging.getLogger(__name__)


NO_SUPPORT = 0
# Used when the device is known to not be supported
IMPROBABLE_SUPPORT = 10
# Used when it is expected the device won't be supported
UNKNOWN_SUPPORT = 20
# Used when not enough information is available to take a decision
PROBABLE_SUPPORT = 30
# Used when it is expected the device will be supported, but we are either
# missing some information, either we don't know for real if this device is
# supported, i.e. no test have been done
INCOMPLETE_SUPPORT = 40
# The device is supported, but in an incomplete way. This might be because
# it's a kind of device that share some similarities but also have some
# difference, or because this would be a completely supported device but we
# did not add explicit support for it
COMPLETE_SUPPORT = 50
# The device is completely supported, i.e. we know it works well, but the
# device might not be in the version we are targeting, but in a version that
# is so closely similar that it makes no difference
FULL_SUPPORT = 60
# The device is exactly what the plugin is targeting.


class IPluginAssociator(Interface):
    def associate(dev_info):
        """Return a 'support score' from a device info object."""


class BasePgAssociator(object):
    implements(IPluginAssociator)
    
    def associate(self, dev_info):
        vendor = dev_info.get(u'vendor')
        if vendor is None:
            return UNKNOWN_SUPPORT
        else:
            model = dev_info.get(u'model')
            version = dev_info.get(u'version')
            return self._do_associate(vendor, model, version)
    
    def _do_associate(self, vendor, model, version):
        """
        Pre: vendor is not None
        """
        raise NotImplementedError('must be overridden in derived class')


class IConflictSolver(Interface):
    def solve(pg_ids):
        """
        Return a pg_id or None if not able to solve the conflict.
        
        Pre: len(pg_ids) > 1
        """


class PreferredConflictSolver(object):
    implements(IConflictSolver)
    
    def __init__(self, preferred_pg_ids):
        self._pref_pg_ids = preferred_pg_ids
    
    def solve(self, pg_ids):
        for pg_id in self._pref_pg_ids:
            if pg_id in pg_ids:
                return pg_id
        return None


class AlphabeticConflictSolver(object):
    implements(IConflictSolver)
    
    def solve(self, pg_ids):
        return min(pg_ids)


class ReverseAlphabeticConflictSolver(object):
    implements(IConflictSolver)
    
    def solve(self, pg_ids):
        return max(pg_ids)


class CompositeConflictSolver(object):
    implements(IConflictSolver)
    
    def __init__(self, solvers):
        self._solvers = solvers
    
    def solve(self, pg_ids):
        for solver in self._solvers:
            pg_id = solver.solve(pg_ids)
            if pg_id:
                return pg_id
        return None


class PluginAssociatorDeviceUpdater(object):
    implements(IDeviceUpdater)
    
    force_update = False
    min_level = PROBABLE_SUPPORT
    
    def __init__(self, pg_mgr, conflict_solver):
        self._pg_mgr = pg_mgr
        self._solver = conflict_solver
    
    def update(self, dev, dev_info, request, request_type):
        logger.debug('In %s', self.__class__.__name__)
        if self.force_update or u'plugin' not in dev:
            pg_id = self._do_update(dev_info)
            if pg_id:
                dev[u'plugin'] = pg_id
        return defer.succeed(False)
    
    def _do_update(self, dev_info):
        pg_scores = self._get_scores(dev_info)
        if pg_scores:
            max_score, pg_ids = max(pg_scores.iteritems(), key=itemgetter(0))
            if max_score >= self.min_level:
                assert pg_ids
                if len(pg_ids) == 1:
                    return pg_ids[0]
                else:
                    pg_id = self._solver.solve(pg_ids)
                    if pg_id:
                        return pg_id
                    else:
                        logger.warning('Conflict resolution yielded nothing for plugins: %s',
                                       pg_ids)
        return None
    
    def _get_scores(self, dev_info):
        pg_scores = defaultdict(list)
        for pg_id, pg in self._pg_mgr.iteritems():
            sstor = pg.pg_associator
            if sstor is not None:
                try:
                    score = sstor.associate(dev_info)
                except Exception:
                    logger.error('Error during plugin association for plugin %s',
                                 pg_id, exc_info=True)
                else:
                    pg_scores[score].append(pg_id)
        return pg_scores
