# -*- coding: UTF-8 -*-

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

import re

OIP_WAITING  = 'waiting'
OIP_PROGRESS = 'progress'
OIP_SUCCESS  = 'success'
OIP_FAIL     = 'fail'


class OperationInProgress(object):
    """Base class for operations in progress.
    
    An operation in progress is a monitor over an underlying operation. It's
    used to expose the status of an underlying operation in a standard way.
    
    Operation in progress instances have the following attributes:
      label -- the label identifying the underlying operation, or None
      state -- the state of the operation; usually one of waiting, progress,
        success or fail
      current -- a non-negative integer representing the current 'step' of
        the operation, or None
      end -- a positive integer representing the last 'step' of the operation,
        or None
      sub_oips -- a list of operation in progress instances representing sub
        operations of the underlying operation
    
    """
    def __init__(self, label=None, state=OIP_WAITING, current=None, end=None, sub_oips=[]):
        self.label = label
        self.state = state
        self.current = current
        self.end = end
        self.sub_oips = list(sub_oips)


def format_oip(oip):
    """Format an operation in progress to a string.
    
    The format is '[label|]state[;current[/end]](\(sub_oips\))*'.
    
    Here's some examples:
      progress
      download|progress
      download|progress;10
      download|progress;10/100
      download|progress(file_1|progress;20/100)(file_2|waiting;0/50)
      download|progress;20/150(file_1|progress)(file_2|waiting)
      op|progress(op1|progress(op1.1|progress)(op.1.2|waiting))(op2|progress)
      
    """
    s = ''
    if oip.label is not None:
        s += '%s|' % oip.label
    s += oip.state
    if oip.current is not None:
        s += ';%s' % oip.current
        if oip.end:
            s += '/%s' % oip.end
    for sub_oip in oip.sub_oips:
        s += '(%s)' % format_oip(sub_oip)
    return s


def _split_top_parentheses(str_):
    idx = 0
    length = len(str_)
    result = []
    while idx < length:
        if str_[idx] != '(':
            raise ValueError('invalid character: %s' % str_[idx])
        start_idx = idx
        idx += 1
        count = 1
        while count:
            if idx >= length:
                raise ValueError('unbalanced number of parentheses: %s' % str_)
            c = str_[idx]
            if c == '(':
                count += 1
            elif c == ')':
                count -= 1
            idx += 1
        end_idx = idx
        result.append(str_[start_idx+1:end_idx-1])
    return result


_PARSE_OIP_REGEX = re.compile(r'^(?:(\w+)\|)?(\w+)(?:;(\d+)(?:/(\d+))?)?')

def parse_oip(oip_string):
    """Return an operation in progress from a string.
    
    Valid strings are the same as the one returned by format_oip.
    
    Raise a ValueError if the string is invalid.
    
    """
    m = _PARSE_OIP_REGEX.search(oip_string)
    if not m:
        raise ValueError('invalid oip string: %s' % oip_string)
    else:
        label, state, raw_current, raw_end = m.groups()
        raw_sub_oips = oip_string[m.end():] 
        current = raw_current if raw_current is None else int(raw_current)
        end = raw_end if raw_end is None else int(raw_end)
        sub_oips = [parse_oip(sub_oip_string) for sub_oip_string in
                    _split_top_parentheses(raw_sub_oips)]
        return OperationInProgress(label, state, current, end, sub_oips)


def operation_in_progres_from_deferred(deferred, label=None):
    """Return an operation in progress where the underlying operation is
    determined by a deferred.
    
    """
    def callback(res):
        oip.state = OIP_SUCCESS
        return res
    def errback(err):
        oip.state = OIP_FAIL
        return err
    oip = OperationInProgress(label, OIP_PROGRESS)
    oip.addCallbacks(callback, errback)
    return oip
