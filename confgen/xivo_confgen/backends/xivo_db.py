# -*- coding: utf8 -*-
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010  Proformatique, Guillaume Bour <gbour@proformatique.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..
"""
import inspect, warnings
warnings.simplefilter('ignore')

from sqlalchemy import *
from sqlalchemy.ext.sqlsoup    import SqlSoup
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql            import select

from backend import Backend


def mapped_set(self, key, value):
	self.__dict__[key] = value

def mapped_iterkeys(self):
	keys = sorted(filter(lambda x: x[0] != '_', self.__dict__))

	for k in keys:
		yield k

	return

def mapped_iteritems(self):
	keys = sorted(filter(lambda x: x[0] != '_', self.__dict__))

	for k in keys:
		yield (k, self.__dict__[k])

	return


def iterable(mode):
	def _iterable(f):
		def single_wrapper(*args, **kwargs):
			ret = f(*args, **kwargs)
			if ret is not None:
				ret.__class__.__getitem__ = lambda self, key: self.__dict__[key]
				ret.__class__.iteritems   = mapped_iteritems

			return ret
				
		def list_wrapper(*args, **kwargs):
			ret = f(*args, **kwargs)
			if isinstance(ret, list) and len(ret) > 0:
				#print dir(ret[0])

				ret[0].__class__.__getitem__ = lambda self, key: self.__dict__[key]
				ret[0].__class__.__setitem__ = mapped_set
				ret[0].__class__.iteritems   = mapped_iteritems
				ret[0].__class__.iterkeys    = mapped_iterkeys

			return ret

		return locals()[mode + '_wrapper']
	return _iterable

class SpecializedHandler(object):
	def __init__(self, db, name):
		self.db   = db
		self.name = name

class SCCPUsersHandler(SpecializedHandler):
	def all(self, commented=None, order=None, **kwargs):
		_s = self.db.usersccp.table
		_u = self.db.userfeatures.table
		_p = self.db.phone.table
		q  = select(
			[_s, _p.c.macaddr, _p.c.model, _p.c.vendor, _u.c.id.label('featid'), _u.c.number, _u.c.description],
			and_(
				_u.c.protocol == 'sccp', 
				_u.c.protocolid == _s.c.id, 
				_u.c.id == _p.c.iduserfeatures
			)
		)

		conn = self.db.engine.connect()
		return conn.execute(q).fetchall()

	@iterable('single')
	def default_line(self, id):
		return self.db.sccpline.filter(self.db.sccpline.id == id).first()


class AgentUsersHandler(SpecializedHandler):
	def all(self, commented=None, order=None, **kwargs):
		_a = self.db.staticagent.table
		_f = self.db.agentfeatures.table
		q  = select(
			[_a.c.var_val, _f.c.autologoff, _f.c.ackcall, _f.c.acceptdtmf, _f.c.enddtmf,
				_f.c.wrapuptime, _f.c.musiconhold],
			and_(
				_a.c.category  == 'agents',
				_a.c.var_name  == 'agent',
				_a.c.id        == _f.c.agentid,
				_f.c.commented == 0
			)
		)

		conn = self.db.engine.connect()
		return conn.execute(q).fetchall()


class QObject(object):
	_translation = {
		'sip'           : ('staticsip',),
		'iax'           : ('staticiax',),
		'sccp'          : ('staticsccp',),
		'voicemail'     : ('staticvoicemail',),
		'queue'         : ('staticqueue',),
		'agent'         : ('staticagent',),
		'meetme'        : ('staticmeetme',),
		'musiconhold'   : ('musiconhold',),
		'features'     	: ('features',),

		'sipauth'       : ('sipauthentication',),
		'iaxcalllimits' : ('iaxcallnumberlimits',),

		'sipusers'      : ('usersip', {'category': 'user'}),
		'iaxusers'      : ('useriax', {'category': 'user'}),
		'sccpusers'     : SCCPUsersHandler,
		'sccplines'     : ('sccpline',),
		'agentusers'    : AgentUsersHandler,

		'siptrunks'     : ('usersip', {'category': 'trunk'}),
		'iaxtrunks'     : ('useriax', {'category': 'trunk'}),

		'voicemails'    : ('voicemail',),
		'queues'        : ('queue',),
		'queuemembers'  : ('queuemember',),
	}

	def __init__(self, db, name):
		self.db   = db
		self.name = name

	@iterable('list')
	def all(self, commented=None, order=None, **kwargs):
		_trans = self._translation.get(self.name, (self.name,))
		q = getattr(self.db, _trans[0])

		## FILTERING
		conds = []
		if isinstance(commented, bool):
			conds.append(q.commented == int(commented))
	
		if len(_trans) > 1:
			for k, v in _trans[1].iteritems():
				conds.append(getattr(q, k) == v)

		for k, v in kwargs.iteritems():
			conds.append(getattr(q, k) == v)

		q = q.filter(and_(*conds))

		## ORDERING
		if order is not None:
			q = q.order_by(order)

		return q.all()


class XivoDBBackend(Backend):
	def __init__(self, uri):
		self.db = SqlSoup(uri)

	def __getattr__(self, name):
		if not name in QObject._translation:
			raise KeyError(name)

		if inspect.isclass(QObject._translation[name]) and\
			 issubclass(QObject._translation[name], SpecializedHandler):
			return QObject._translation[name](self.db, name)

		return QObject(self.db, name)

