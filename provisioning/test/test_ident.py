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

import unittest
from provd.devices.ident import *

# XXX I forgot that unittest could't work with deferred since unittest
#     use exceptions and exception does not reach the code which
#     attached the callback/errback. So, right now, only way to know if
#     the tests passed is to check if there's any 'unhandled exception
#     in deferred' after running the tests.

class TestCollaboratingDevInfoXtor(unittest.TestCase):
    def test_first_seen_updater_ignore_on_conflict(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v2'}), ]

        collab_xtor = CollaboratingDeviceInfoExtractor(FirstSeenUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)

    def test_first_seen_updater_noop_on_nonconflict(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k2': 'v2'}), ]

        collab_xtor = CollaboratingDeviceInfoExtractor(FirstSeenUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1', 'k2': 'v2'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)

    def test_last_seen_updater_set_on_conflict(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v2'}), ]

        collab_xtor = CollaboratingDeviceInfoExtractor(LastSeenUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v2'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)

    def test_last_seen_updater_noop_on_nonconflict(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k2': 'v2'}), ]

        collab_xtor = CollaboratingDeviceInfoExtractor(LastSeenUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1', 'k2': 'v2'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)

    def test_remove_updater_removes_all_occurences_on_conflict(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v2'}),
                 StaticDeviceInfoExtractor({'k1': 'v3'})]

        collab_xtor = CollaboratingDeviceInfoExtractor(RemoveUpdater, xtors)
        def call(dev_info):
            self.assertEqual({}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)

    def test_remove_updater_noop_on_nonconflict(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k2': 'v2'}), ]

        collab_xtor = CollaboratingDeviceInfoExtractor(RemoveUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1', 'k2': 'v2'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)

    def test_remove_updater_noop_on_key_conflict_but_no_value_conflict(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v1'}), ]

        collab_xtor = CollaboratingDeviceInfoExtractor(RemoveUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)

    def test_voting_updater_votes_for_only_if_only_one(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}), ]

        collab_xtor = CollaboratingDeviceInfoExtractor(RemoveUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)

    def test_voting_updater_votes_for_highest_1(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v2'}), ]

        collab_xtor = CollaboratingDeviceInfoExtractor(VotingUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)

    def test_voting_updater_votes_for_highest_2(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v2'}),
                 StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v1'}), ]

        collab_xtor = CollaboratingDeviceInfoExtractor(VotingUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)
