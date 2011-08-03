# vim: set fileencoding=utf-8 :
# XiVO CTI Server

__version__   = '$Revision$'
__date__      = '$Date$'
__copyright__ = 'Copyright (C) 2011 Proformatique'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This scheduler has been originally inspired from the MIT licensed
# APScheduler, although they don't share much in common, except for
# the name of some public methods.
#
# The biggest issue with APScheduler was that it had no support for
# aware datetime, nor for naive UTC datetime.
#
# There was also a subtle bug in the concurrency handling which could
# make a scheduled job now to be fired at its due time.

import datetime
import heapq
import logging
import threading
import pytz

logger = logging.getLogger(__name__)


class _Job(object):
    def __init__(self, job_id, utc_datetime, func, args, kwargs):
        self.job_id = job_id
        self.utc_datetime = utc_datetime
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def __lt__(self, other):
        try:
            if self.utc_datetime < other.utc_datetime:
                return True
            elif self.utc_datetime == other.utc_datetime:
                return NotImplemented
            else:
                return False
        except AttributeError:
            return TypeError('Job_ can only be compared with other job objects')
    
    def __repr__(self):
        return '<_Job(%s, datetime=%s)>' % (self.job_id, self.utc_datetime)


class Scheduler(object):
    """A simple scheduler that can schedule callable object to be called in
    the future.
    
    Note that the job are run in the scheduler thread so you do not want to
    take too much time in the callback or you might delay the other jobs.
    
    This class is not thread safe, i.e. it's start/shutdown/add_job/remove_job
    are not thread safe. (in fact, the remove method is thread-safe). That
    said, they can be used from the scheduler thread, but this means you must
    take some external precaution.
    
    This class also accept datetimes that are not UTC localized, as long as
    they are localized.
    
    """
    
    _ADD_MSG = 'add'
    _REMOVE_MSG = 'remove'
    
    def __init__(self, daemonic=True):
        """
        daemonic -- the daemonic status of the scheduler thread
        """
        self.daemonic = daemonic
        self._condition = threading.Condition()
        self._id_generator = self._new_id_generator()
        # this data structure is used to exchange data between the scheduler
        # loop and the add/remove function
        self._msgs = []
        self._stopped = True
        self._thread = None
        # this date structures are only modified by the scheduler thread
        self._jobs = []
    
    def _new_id_generator(self, start=1):
        n = start
        while True:
            yield str(n)
            n += 1 
    
    def start(self):
        if self.running:
            logger.info('Scheduler is already started')
            return
        
        logger.debug('Starting scheduler')
        self._stopped = False
        self._thread = threading.Thread(target=self._main_loop, name='Scheduler')
        self._thread.setDaemon(self.daemonic)
        self._thread.start()
    
    def shutdown(self, wait=True):
        """
        
        You can shutdown the scheduler from the scheduler thread but you
        MUST use wait=False.
        
        """
        if not self.running:
            return
        
        logger.debug('Shutting down scheduler')
        with self._condition:
            self._stopped = True
            self._condition.notify()
        
        if wait:
            self._thread.join()
    
    @property
    def running(self):
        return not self._stopped and self._thread and self._thread.isAlive()
    
    def add_job(self, utc_datetime, func, args=None, kwargs=None):
        """Return an opaque job ID, the only guaranteed being that it's a
        string and it's unique for the lifetime of the scheduled job.
        
        """
        job = self._new_job(utc_datetime, func, args, kwargs)
        msg = (self._ADD_MSG, (job,))
        self._queue_msg(msg)
        return job.job_id
    
    def _new_job(self, utc_datetime, func, args, kwargs):
        job_id = self._id_generator.next()
        return _Job(job_id, utc_datetime, func, args, kwargs)
    
    def _queue_msg(self, msg):
        with self._condition:
            self._msgs.append(msg)
            self._condition.notify()
    
    def remove_job(self, job_id):
        msg = (self._REMOVE_MSG, (job_id,))
        self._queue_msg(msg)
    
    def _main_loop(self):
        logger.info('Scheduler started')
        timeout = self._compute_next_timeout()
        
        while True:
            # be extremely careful if you modify the next few lines if you
            # don't want potentially wrong behaviour to pop up
            with self._condition:
                if not self._msgs and not self._stopped:
                    # no new messages and not stopped, so let's wait
                    self._condition.wait(timeout)
                new_msgs = self._msgs
                self._msgs = []
            
            logger.debug('Scheduler loop processing')
            if self._stopped:
                break
            self._process_new_msgs(new_msgs)
            self._execute_due_jobs()
            timeout = self._compute_next_timeout()
        
        logger.info('Scheduler has been shut down')
    
    def _process_new_msgs(self, new_msgs):
        # NOTE: to be called only from the scheduler thread
        for msg in new_msgs:
            try:
                msg_type, msg_data = msg
                fun_name = '_process_msg_' + msg_type
                try:
                    fun = getattr(self, fun_name)
                except AttributeError:
                    logger.error('Unknown message passed to main loop: %s', msg)
                else:
                    fun(msg_data)
            except Exception:
                logger.error('Error while processing message %s', msg, exc_info=True)
    
    def _process_msg_add(self, msg_data):
        # This method is called 'dynamically' by the _process_new_msgs method
        # NOTE: to be called only from the scheduler thread
        job, = msg_data
        idx = self._find_job(job.job_id)
        if idx != -1:
            logger.error('Could not schedule job %s because ID already in use',
                         job)
        else:
            logger.debug('Inserting job %s', job)
            heapq.heappush(self._jobs, job)
    
    def _process_msg_remove(self, msg_data):
        # This method is called 'dynamically' by the _process_new_msgs method
        # NOTE: to be called only from the scheduler thread
        job_id, = msg_data
        idx = self._find_job(job_id)
        if idx == -1:
            logger.debug('No job with ID %s', job_id)
        else:
            logger.debug('Removing job with ID %s', job_id)
            # It's unfortunate the heapq module doesn't provide a function to
            # remove an arbitrary element from a heap. That said, since removing
            # a job should not be the most frequent operation, I guess this
            # maybe not too efficient solution is fine
            del self._jobs[idx]
            heapq.heapify(self._jobs)
    
    def _find_job(self, job_id):
        # Return the idx at which job with the given ID can be found
        # NOTE: to be called only from the scheduler thread
        for idx, job in enumerate(self._jobs):
            if job.job_id == job_id:
                return idx
        return -1
    
    def _execute_due_jobs(self):
        # NOTE: to be called only from the scheduler thread
        while self._jobs:
            # we are getting the time at each loop because we are not using
            # a threadpool so the 'now' could vary a bit
            utc_now = pytz.utc.localize(datetime.datetime.utcnow())
            if self._jobs[0].utc_datetime > utc_now:
                break
            job = heapq.heappop(self._jobs)
            try:
                logger.debug('Executing job %s at %s', job, utc_now)
                args = () if job.args is None else job.args
                kwargs = {} if job.kwargs is None else job.kwargs
                job.func(*args, **kwargs)
            except Exception:
                logger.error('Error while executing job %s', job, exc_info=True)
    
    def _compute_next_timeout(self):
        # Return a floating point representing the number of seconds to wait before
        # needing to execute the next job
        # NOTE: to be called only from the scheduler thread
        if not self._jobs:
            return None
        else:
            utc_now = pytz.utc.localize(datetime.datetime.utcnow())
            delta = self._jobs[0].utc_datetime - utc_now
            return delta.days * 86400 + delta.seconds + delta.microseconds / 1000000.0
