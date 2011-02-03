# -*- coding: UTF-8 -*-

__version__ = "$Revision $ $Date$"
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

# NOTE: these tests are not automated (yet). You need to manually check
#       the output of each test and compare it with the expected output...

import time
from prov.synchro import DeferredRWLock
from twisted.internet import defer
from twisted.internet import reactor

_load_time = time.time()
def _time_since_load():
    return time.time() - _load_time


class TracingDeferred(defer.Deferred):
    def __init__(self, id):
        self._id = id
        print u'%.4f <%2s> Constructing' % (_time_since_load(), self._id)
        defer.Deferred.__init__(self)
    
    def callback(self, result):
        print u'%.4f <%2s> Before callback' % (_time_since_load(), self._id)
        defer.Deferred.callback(self, result)


def coroutine(fun):
    def aux(*args, **kwargs):
        cr = fun(*args, **kwargs)
        cr.next()
        return cr
    return aux


@coroutine
def gen_fixed_deferred(delay=1.0):
    id = yield
    while True:
        d = TracingDeferred(id)
        reactor.callLater(delay, d.callback, None)
        id = yield d


@coroutine
def gen_incr_fixed_deferred(delay=1.0, incr=0.2):
    id = yield
    while True:
        d = TracingDeferred(id)
        reactor.callLater(delay, d.callback, None)
        id = yield d
        delay += incr


def rw_lock_test_no_write_while_read(deferred_generator):
    # Expected output:
    #   <r1> Constructing
    #   <r1> Before callback
    #   <w1> Constructing
    #   <w1> Before callback
    deferreds = []
    rw_lock = DeferredRWLock()
    deferreds.append(rw_lock.read_lock.run(deferred_generator.send, 'r1'))
    deferreds.append(rw_lock.write_lock.run(deferred_generator.send, 'w1'))
    dl = defer.DeferredList(deferreds)
    return dl


def rw_lock_test_read_more_while_read_and_no_write_wait(deferred_generator):
    # Expected output:
    #   <r1> Constructing
    #   <r2> Constructing
    #   <r1> Before callback
    #   <r2> Before callback
    deferreds = []
    rw_lock = DeferredRWLock()
    deferreds.append(rw_lock.read_lock.run(deferred_generator.send, 'r1'))
    deferreds.append(rw_lock.read_lock.run(deferred_generator.send, 'r2'))
    dl = defer.DeferredList(deferreds)
    return dl


def rw_lock_test_no_write_while_write(deferred_generator):
    # Expected output:
    #   <w1> Constructing
    #   <w1> Before callback
    #   <w2> Constructing
    #   <w2> Before callback
    deferreds = []
    rw_lock = DeferredRWLock()
    deferreds.append(rw_lock.write_lock.run(deferred_generator.send, 'w1'))
    deferreds.append(rw_lock.write_lock.run(deferred_generator.send, 'w2'))
    dl = defer.DeferredList(deferreds)
    return dl


def rw_lock_privelege_writers(deferred_generator):
    # Expected output:
    #   <w1> Constructing
    #   <w1> Before callback
    #   <w2> Constructing
    #   <w2> Before callback
    #   <r1> Constructing
    #   <r1> Before callback
    deferreds = []
    rw_lock = DeferredRWLock()
    deferreds.append(rw_lock.write_lock.run(deferred_generator.send, 'w1'))
    deferreds.append(rw_lock.read_lock.run(deferred_generator.send, 'r1'))
    deferreds.append(rw_lock.write_lock.run(deferred_generator.send, 'w2'))
    dl = defer.DeferredList(deferreds)
    return dl


def rw_lock_schedule_all_readers_if_possible(deferred_generator):
    # Expected output:
    #   <w1> Constructing
    #   <w1> Before callback
    #   <r1> Constructing
    #   <r2> Constructing
    #   <r1> Before callback
    #   <r2> Before callback
    deferreds = []
    rw_lock = DeferredRWLock()
    deferreds.append(rw_lock.write_lock.run(deferred_generator.send, 'w1'))
    deferreds.append(rw_lock.read_lock.run(deferred_generator.send, 'r1'))
    deferreds.append(rw_lock.read_lock.run(deferred_generator.send, 'r2'))
    dl = defer.DeferredList(deferreds)
    return dl


def rw_lock_tests():
    # Schedule all the tests and call reactor.stop when all tests are done
    deferreds = []
    lock = defer.DeferredLock()
    for test_fun in [rw_lock_test_no_write_while_read,
                     rw_lock_test_read_more_while_read_and_no_write_wait,
                     rw_lock_test_no_write_while_write,
                     rw_lock_privelege_writers,
                     rw_lock_schedule_all_readers_if_possible]: 
        def wrap_test(test_fun_):
            deferred_generator = gen_incr_fixed_deferred()
            print '\n== Starting test %s ==' % test_fun_.__name__
            d = test_fun_(deferred_generator)
            return d
        deferreds.append(lock.run(wrap_test, test_fun))
    dl = defer.DeferredList(deferreds)
    dl.addCallback(lambda _: reactor.stop())


if __name__ == '__main__':
    rw_lock_tests()
    reactor.run()
