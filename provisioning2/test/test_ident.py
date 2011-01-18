# -*- coding: UTF-8 -*-

import unittest
from prov2.devices.ident import *


# XXX I forgot that unittest could't work with deferred since unittest
#     use exceptions and exception does not reach the code which
#     attached the callback/errback. So, right now, only way to know if
#     the tests passed is to check if there's any 'unhandled exception
#     in deferred' after running the tests.

class TestCollaboratingDevInfoXtor(unittest.TestCase):
    def test_first_seen_updater_ignore_on_conflict(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v2'}),]
        
        collab_xtor = CollaboratingDeviceInfoExtractor(FirstSeenUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)
    
    def test_first_seen_updater_noop_on_nonconflict(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k2': 'v2'}),]
        
        collab_xtor = CollaboratingDeviceInfoExtractor(FirstSeenUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1', 'k2': 'v2'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)
        
    def test_last_seen_updater_set_on_conflict(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v2'}),]
        
        collab_xtor = CollaboratingDeviceInfoExtractor(LastSeenUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v2'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)
    
    def test_last_seen_updater_noop_on_nonconflict(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k2': 'v2'}),]
        
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
                 StaticDeviceInfoExtractor({'k2': 'v2'}),]
        
        collab_xtor = CollaboratingDeviceInfoExtractor(RemoveUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1', 'k2': 'v2'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)
    
    def test_remove_updater_noop_on_key_conflict_but_no_value_conflict(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v1'}),]
        
        collab_xtor = CollaboratingDeviceInfoExtractor(RemoveUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)
    
    def test_voting_updater_votes_for_only_if_only_one(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),]
        
        collab_xtor = CollaboratingDeviceInfoExtractor(RemoveUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)
        
    def test_voting_updater_votes_for_highest_1(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v2'}),]
        
        collab_xtor = CollaboratingDeviceInfoExtractor(VotingUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)
    
    def test_voting_updater_votes_for_highest_2(self):
        xtors = [StaticDeviceInfoExtractor({'k1': 'v2'}),
                 StaticDeviceInfoExtractor({'k1': 'v1'}),
                 StaticDeviceInfoExtractor({'k1': 'v1'}),]
        
        collab_xtor = CollaboratingDeviceInfoExtractor(VotingUpdater, xtors)
        def call(dev_info):
            self.assertEqual({'k1': 'v1'}, dev_info)
        def err(failure):
            self.fail(failure)
        collab_xtor.extract(None, None).addCallbacks(call, err)
