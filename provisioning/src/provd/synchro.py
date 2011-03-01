# -*- coding: UTF-8 -*-

"""Synchronization primitives for event driven systems."""

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

# TODO add support for cancel

import logging
from collections import deque
from twisted.internet import defer

logger = logging.getLogger(__name__)


class InvalidLockUsage(Exception):
    pass


class _DeferredRWLock_Base(object):
    def __init__(self, acquire_fun, release_fun):
        self._acquire_fun = acquire_fun
        self._release_fun = release_fun
    
    def acquire(self):
        return self._acquire_fun()
    
    def _releaseAndReturn(self, r):
        self.release()
        return r
    
    def run(self, f, *args, **kwargs):
        def execute(ignoredResult):
            d = defer.maybeDeferred(f, *args, **kwargs)
            d.addBoth(self._releaseAndReturn)
            return d

        d = self.acquire()
        d.addCallback(execute)
        return d

    def release(self):
        self._release_fun()


class DeferredRWLock(object):
    """A read-write lock for event driven systems.
    
    Instances of this class have the following attributes:
      read_lock -- the read lock
      write_lock -- the write lock
    
    Both locks have the same interface as the twisted.internet.defer.DeferredLock.
    
    Writers are privileged. No support for re-entry, since it's impossible
    without adding explicit 'task' identifier.
    
    """
    def __init__(self):
        self._read_waiting = deque()
        self._write_waiting = deque()
        self._reading = 0
        self._writing = 0
        self.read_lock = _DeferredRWLock_Base(self._acquire_read_lock,
                                              self._release_read_lock)
        self.write_lock = _DeferredRWLock_Base(self._acquire_write_lock,
                                               self._release_write_lock)
    
    def _acquire_read_lock(self):
        logger.debug('Waiting for read lock acquisition of RWLock %s', self)
        d = defer.Deferred()
        self._read_waiting.append(d)
        self._reschedule()
        return d
    
    def _acquire_write_lock(self):
        logger.debug('Waiting for write lock acquisition of RWLock %s', self)
        d = defer.Deferred()
        self._write_waiting.append(d)
        self._reschedule()
        return d
    
    def _unlock_all_readers(self):
        assert self._read_waiting
        while self._read_waiting:
            logger.debug('Acquiring read lock %d of RWLock %s', self._reading, self)
            self._reading += 1
            d = self._read_waiting.popleft()
            d.callback(self)
    
    def _unlock_one_writer(self):
        assert self._write_waiting
        logger.debug('Acquiring write lock %d of RWLock %s', self._writing, self)
        self._writing += 1
        d = self._write_waiting.popleft()
        d.callback(self)
    
    def _reschedule(self):
        # Check if we can fire new callbacks
        if self._reading:
            assert not self._writing
            # someone is reading...
            if self._write_waiting:
                # ...and someone is waiting for write 
                # do nothing
                pass
            elif self._read_waiting:
                assert not self._write_waiting
                # ...and no one is waiting for write yet some are waiting for read
                # It might looks like an error, but we need to consider how lock
                # acquisition is done, i.e. by queuing and calling this method
                self._unlock_all_readers()
            else:
                # ...and no writers or readers are waiting
                # do nothing
                pass
        elif self._writing:
            assert not self._reading
            # someone is writing...
            # do nothing
            pass
        else:
            # no one is reading nor writing...
            if self._write_waiting:
                # ...and someone is waiting for write
                self._unlock_one_writer()
            elif self._read_waiting:
                assert not self._write_waiting
                # ...and someone is waiting for read while no one is waiting for write
                self._unlock_all_readers()
            else:
                # ...and no writers or readers are waiting
                # do nothing
                pass

    def _release_read_lock(self):
        if not self._reading:
            raise InvalidLockUsage('read lock released while no one was reading')
        logger.debug('Releasing read lock %d of RWLock %s', self._reading - 1, self)
        self._reading -= 1
        self._reschedule()
    
    def _release_write_lock(self):
        if not self._writing:
            raise InvalidLockUsage('write lock released while no one was writing')
        logger.debug('Releasing write lock %d of RWLock %s', self._writing - 1, self)
        self._writing -= 1
        self._reschedule()
