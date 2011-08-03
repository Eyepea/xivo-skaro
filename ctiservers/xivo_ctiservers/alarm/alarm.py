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

import datetime
import errno
import logging
import json
import os
import re
import threading
import pytz

logger = logging.getLogger(__name__)


_ALARM_CLOCK_REGEX = re.compile(r'^(\d\d):(\d\d)$')

def _parse_alarm_clock(alarm_clock):
    """Return a (hour, minute) tuple from an alarm clock string.
    
    Raise a ValueError if the alarm clock is invalid.
    
    >>> parse_alarm_clock('06:44')
    (6, 44)
    
    """
    m = _ALARM_CLOCK_REGEX.match(alarm_clock)
    if not m:
        raise ValueError('invalid alarm clock: %s', alarm_clock)
    hour, minute = map(int, m.group(1, 2))
    if hour >= 24:
        raise ValueError('invalid hour: %s', hour)
    if minute >= 60:
        raise ValueError('invalid minute: %s', minute)
    return hour, minute


_ONE_DAY = datetime.timedelta(days=1)

def _compute_due_datetime(alarm_clock, zone, utc_now=None):
    """Return an UTC localized due datetime from an alarm clock string and
    a timezone name.
    
    The utc_now parameter is used if you want to use an arbitrary reference
    time instead of the real now. Mostly for testing purpose.
    
    >>> now = pytz.utc.localize(datetime.datetime(2011, 11, 4, 17, 00))
    >>> _compute_due_datetime('06:44', 'America/Montreal', now)
    datetime.datetime(2011, 11, 5, 10, 44, tzinfo=<UTC>)
    >>> # DST change on 2011-11-06 02:00 for America/Montreal
    >>> now = pytz.utc.localize(datetime.datetime(2011, 11, 5, 17, 00))
    >>> _compute_due_datetime('06:44', 'America/Montreal', now)
    datetime.datetime(2011, 11, 6, 11, 44, tzinfo=<UTC>)
    
    """
    # NOTE: we are using naive datetime in the process because adding
    # one day to an aware timezone really means adding 24 hours, which is
    # not what we want if there's a DST change during these 24 hours
    alarm_hour, alarm_minute = _parse_alarm_clock(alarm_clock)
    
    loc_timezone = pytz.timezone(zone)
    if utc_now is None:
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    loc_now = utc_now.astimezone(loc_timezone)
    loc_now_naive = loc_now.replace(tzinfo=None)
    
    loc_alarm_naive = loc_now_naive.replace(hour=alarm_hour, minute=alarm_minute,
                                            second=0, microsecond=0)
    if loc_alarm_naive < loc_now_naive:
        # schedule alarm for the next day
        loc_alarm_naive += _ONE_DAY
    
    loc_alarm = loc_timezone.localize(loc_alarm_naive)
    utc_alarm = loc_alarm.astimezone(pytz.utc)
    return utc_alarm


_FORMAT = '%Y-%m-%d %H:%M'

def _utc_datetime_to_string(utc_datetime):
    # WARNING: datetime must be in UTC or you'll lose information
    assert utc_datetime.tzinfo == pytz.UTC or utc_datetime.tzinfo is None
    return utc_datetime.strftime(_FORMAT)


def _string_to_utc_datetime(string):
    # Return an UTC localized datetime
    return pytz.utc.localize(datetime.datetime.strptime(string, _FORMAT))


def get_system_zone():
    with open('/etc/timezone') as fobj:
        return fobj.read().rstrip()


class AlarmClockManager(object):
    def __init__(self, scheduler, persister, callback, default_zone=None):
        self._sched = scheduler
        self._persister = persister
        self._callback = callback
        self._default_zone = default_zone
        # a dictionary mapping userid to scheduler job ID
        self._alarms = {}
        self._lock = threading.Lock()
        self._load_persisted_alarm()
    
    def _load_persisted_alarm(self):
        for userid, utc_datetime, data in self._persister.list():
            logger.info('Loaded persisted alarm for user %s', userid)
            self._add_alarm(userid, utc_datetime, data, persist=False)
    
    def _add_alarm(self, userid, utc_datetime, data, persist=True):
        with self._lock:
            job_id = self._sched.add_job(utc_datetime, self._alarm_callback, (data,))
            self._alarms[userid] = job_id
            if persist:
                self._persister.add(userid, utc_datetime, data)
    
    def _try_cancel_alarm(self, userid):
        # Cancel alarm if it has not yet run/if it is present
        with self._lock:
            if userid in self._alarms:
                job_id = self._alarms.pop(userid)
                self._sched.remove_job(job_id)
                self._persister.remove(userid)
            else:
                logger.debug('Ignoring cancel for user %s since no alarm is set',
                             userid)
    
    def update_alarm_clock(self, userid, alarm_clock, zone=None):
        """
        userid -- the user ID (userfeaturesid) as an integer, i.e. 2 for example
        alarm_clock -- an alarm clock specification, i.e. '06:44' for example,
          or an empty string
        zone -- a timezone name, i.e. 'America/Montreal' for example. If it
          evaluates to false, use the default zone
        """
        logger.info('Updating alarm clock to %s (%s) for user %s', alarm_clock,
                    zone, userid)
        if not alarm_clock:
            logger.debug('Cancelling alarm for user %s', userid)
            self._try_cancel_alarm(userid)
        else:
            logger.debug('Setting alarm for user %s', userid)
            # cancel any pending alarm for user
            self._try_cancel_alarm(userid)
            
            # add a new alarm
            if not zone:
                if self._default_zone is None:
                    raise Exception('no zone given and no default zone set')
                else:
                    zone = self._default_zone
            utc_datetime = _compute_due_datetime(alarm_clock, zone)
            data = {'userid': userid}
            self._add_alarm(userid, utc_datetime, data)
            logger.info('Alarm scheduled at %s for user %s', utc_datetime, userid)
    
    def _alarm_callback(self, data):
        # WARNING: we are in the scheduler thread
        userid = data['userid']
        logger.info('Alarm fired at %s for user %s', datetime.datetime.utcnow(),
                    userid)
        with self._lock:
            # userid won't be in self._alarms if we cancelled the alarm at
            # about the same time it was fired
            if userid in self._alarms:
                del self._alarms[userid]
                self._persister.remove(userid)
        self._callback(data)


class NullPersister(object):
    """An alarm persister that doesn't persist alarm."""
    def add(self, userid, utc_datetime, data):
        pass
    
    def remove(self, userid):
        pass
    
    def list(self):
        return []


class JSONPersister(object):
    """An alarm persister that persist alarm into JSON document, one document
    per user.
    
    """
    def __init__(self, directory):
        self._directory = directory
        self._test_mkdir = True
    
    def add(self, userid, utc_datetime, data):
        logger.debug('Persisting alarm for user %s', userid)
        filename = self._get_filename(userid)
        content = {'utc_datetime': _utc_datetime_to_string(utc_datetime),
                   'data': data}
        self._mkdir_if_missing()
        with open(filename, 'w') as fobj:
            json.dump(content, fobj)
    
    def _mkdir_if_missing(self):
        if self._test_mkdir:
            if not os.path.isdir(self._directory):
                os.mkdir(self._directory)
            self._test_mkdir = False
    
    def _get_filename(self, userid):
        return os.path.join(self._directory, str(userid))
    
    def remove(self, userid):
        logger.debug('Removing persisted alarm for user %s', userid)
        filename = self._get_filename(userid)
        try:
            os.remove(filename)
        except OSError, e:
            if e.errno == errno.ENOENT:
                logger.info('No scheduled alarm persisted for user %s', userid)
            else:
                raise
    
    def list(self):
        self._mkdir_if_missing()
        for filename in os.listdir(self._directory):
            abs_filename = os.path.join(self._directory, filename)
            try:
                with open(abs_filename) as fobj:
                    content = json.load(fobj)
                utc_datetime = _string_to_utc_datetime(content['utc_datetime'])
                yield int(filename), utc_datetime, content['data']
            except Exception:
                logger.error('Error while loading persisted alarm %s',
                             abs_filename, exc_info=True)


class MaxDeltaPersisterDecorator(object):
    """An alarm persister decorator that filter alarm clock based on their
    overdue time.
    
    The rationale behind this is that if for a reason or another there's a
    persisted alarm clock that was due 12 hours ago, instead of scheduling
    it so it will be executed now, i.e. 12 hours after its due time, we might
    as well just cancel it.
    
    """
    def __init__(self, max_delta, persister):
        """
        max_delta -- a datetime.timedelta object representing the maximum
          amount of time an overdue job will still be scheduled
        """
        self._max_delta = max_delta
        self._persister = persister
    
    def add(self, userid, utc_datetime, data):
        self._persister.add(userid, utc_datetime, data)
    
    def remove(self, userid):
        self._persister.remove(userid)
    
    def list(self):
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        for userid, utc_datetime, data in self._persister.list():
            delta = utc_now - utc_datetime
            if delta > self._max_delta:
                logger.warning('Persisted alarm for user %s is expired: %s > %s',
                               userid, delta, self._max_delta)
                self._persister.remove(userid)
            else:
                yield userid, utc_datetime, data
