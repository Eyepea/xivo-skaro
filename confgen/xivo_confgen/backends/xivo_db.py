# -*- coding: utf8 -*-
__version__ = "$Revision$ $Date$"
__author__  = "Guillaume Bour <gbour@proformatique.com>"
__license__ = """
    Copyright (C) 2010-2011 Proformatique, Guillaume Bour <gbour@proformatique.com>

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
from sqlalchemy.sql.expression import and_, cast, alias, Alias
from sqlalchemy.sql.functions  import coalesce
from sqlalchemy.sql            import select
from sqlalchemy.types          import VARCHAR
from sqlalchemy.orm            import scoped_session, sessionmaker
from sqlalchemy                import exc

from xivo_confgen.backend import Backend


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
            try:
                ret = f(*args, **kwargs)
            except exc.OperationalError:
                # reconnect & retry
                args[0].db.flush()
                ret = f(*args, **kwargs)

            if ret is not None:
                ret.__class__.__getitem__ = lambda self, key: self.__dict__[key]
                ret.__class__.iteritems   = mapped_iteritems

            return ret
                
        def list_wrapper(*args, **kwargs):
            try:
                ret = f(*args, **kwargs)
            except exc.OperationalError:
                # reconnect & retry
                args[0].db.flush()
                ret = f(*args, **kwargs)


            if isinstance(ret, list) and len(ret) > 0:
                ret[0].__class__.__getitem__  = lambda self, key: self.__dict__[key]
                ret[0].__class__.__setitem__  = mapped_set
                ret[0].__class__.__contains__ = lambda self, key: self.__dict__.__contains__(key)
                ret[0].__class__.iteritems    = mapped_iteritems
                ret[0].__class__.iterkeys     = mapped_iterkeys
                ret[0].__class__.get          = lambda self, key, dft: self.__dict__[key] if key in self.__dict__ else dft

            return ret

        def join_wrapper(*args, **kwargs):
            ret = f(*args, **kwargs)
            if isinstance(ret, list) and len(ret) > 0:
                def find(d, k):
                    #print d.keys, k, k in d, unicode(k) in d
                    return None
                ret[0].__class__.__getitem__ = lambda self, key: find(self.__dict__, key)

            return ret

        return locals()[mode + '_wrapper']
    return _iterable


class SpecializedHandler(object):
    def __init__(self, db, name):
        self.db   = db
        self.name = name

    def execute(self, q):
        try:
            ret = self.db.engine.connect().execute(q)
        except exc.OperationalError:
            # reconnect & retry
            self.db.flush()
            ret = self.db.engine.connect().execute(q)

        return ret


class SCCPUsersHandler(SpecializedHandler):
    def all(self, commented=None, order=None, **kwargs):
        #TODO: fix query (phone <-> line relation)
        (_s, _u, _p) = [getattr(self.db, o)._table for o in
                ('usersccp','linefeatures','devicefeatures')]
        q  = select(
            [_s, _p.c.mac, _p.c.model, _p.c.vendor, _u.c.id.label('featid'), _u.c.number, _u.c.description],
            and_(
                _u.c.protocol   == 'sccp',
                _u.c.protocolid == _s.c.id,
                _u.c.device     == cast(_p.c.id, VARCHAR(32))
            )
        )

        return self.execute(q).fetchall()

    @iterable('single')
    def default_line(self, id):
        return self.db.sccpline.filter(self.db.sccpline.id == id).first()


class AgentUsersHandler(SpecializedHandler):
    def all(self, commented=None, order=None, **kwargs):
        (_a, _f) = [getattr(self.db, o)._table for o in	('staticagent','agentfeatures')]
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

        return self.execute(q).fetchall()


class UserQueueskillsHandler(SpecializedHandler):
    def all(self, *args, **kwargs):
        """
        NOTE: we generate the same queueskills for each line of the user
        """
        (_u, _s,_l) = [getattr(self.db, o)._table.c for o in ('userqueueskill',
            'queueskill','linefeatures')]

        q = select(
            [_s.name, _u.weight, _l.id],
            and_(_u.userid == _l.iduserfeatures, _u.skillid == _s.id)
        )
        q = q.order_by(_u.userid)

        return self.execute(q).fetchall()


class AgentQueueskillsHandler(SpecializedHandler):
    def all(self, *args, **kwargs):
        (_a, _f, _s) = [getattr(self.db, o)._table for o in ('agentqueueskill',	'agentfeatures', 'queueskill')]
        q = select(
            [_f.c.id, _s.c.name, _a.c.weight],
            and_(_a.c.agentid == _f.c.id, _a.c.skillid == _s.c.id)
        )
        q = q.order_by(_f.c.id)

        return self.execute(q).fetchall()


class ExtenumbersHandler(SpecializedHandler):
    def all(self, features=[], *args, **kwargs):
        #NOTE: sqlalchemy 4: table, 5: _table
        (_n, _e) = [getattr(self.db, o)._table for o in ('extenumbers','extensions')] 
        q = select(
            [_n.c.typeval, _n.c.exten, _e.c.commented],
            and_(_n.c.typeval == _e.c.name, _e.c.context == 'xivo-features', _n.c.type == 'extenfeatures',
                _n.c.typeval.in_(features))
        )

        return self.execute(q).fetchall()


class HintsHandler(SpecializedHandler):
    def all(self, *args, **kwargs):
        # get users with hint
        (_u, _v, _l) = [getattr(self.db, o)._table for o in
                ('userfeatures','voicemail','linefeatures')]

        conds = [_u.c.id == _l.c.iduserfeatures, _l.c.internal == 0, _u.c.enablehint == 1]
        if 'context' in kwargs:
            print kwargs['context']
            conds.append(_l.c.context == kwargs['context'])

        q = select(
            [_u.c.id,_l.c.number,_l.c.name,_l.c.protocol,_u.c.enablevoicemail,_v.c.uniqueid],
            and_(*conds),
            from_obj=[
                _u.outerjoin(_v, _u.c.voicemailid == _v.c.uniqueid)
            ],
        )

        return self.execute(q).fetchall()


class PhonefunckeysHandler(SpecializedHandler):
    def all(self, *args, **kwargs):
        # get all supervised user/group/queue/meetme
        (_u, _p, _e, _l) = [getattr(self.db, o)._table for o in
                ('userfeatures','phonefunckey','extenumbers','linefeatures')]
        conds = [
            _l.c.iduserfeatures  == _p.c.iduserfeatures, 
            _p.c.typeextenumbers == None, 
            _p.c.typevalextenumbers == None, 
            _p.c.typeextenumbersright.in_(('user','group','queue','meetme')), 
            _p.c.supervision == 1,
        ]
        if 'context' in kwargs:
            conds.append(_l.c.context == kwargs['context'])

        q = select(
            [_p.c.typeextenumbersright, _p.c.typevalextenumbersright, _e.c.exten],
            and_(*conds),
            from_obj=[
                _p.outerjoin(_e, and_(
                    cast(_p.c.typeextenumbersright, VARCHAR(255)) == cast(_e.c.type, VARCHAR(255)), 
                    _p.c.typevalextenumbersright == _e.c.typeval))],
        )

        return self.execute(q).fetchall()


class BSFilterHintsHandler(SpecializedHandler):
    def all(self, *args, **kwargs):
        # get all supervised bsfilters
        (_u, _p, _e, _l) = [getattr(self.db, o)._table for o in
                ('userfeatures','phonefunckey','extenumbers','linefeatures')]

        _l2 = alias(_l)

        conds = [
            _l.c.iduserfeatures                          == _p.c.iduserfeatures, 
            _p.c.typeextenumbers                         == 'extenfeatures',
            _p.c.typevalextenumbers                      == 'bsfilter', 
            _p.c.typeextenumbersright                    == 'user',
            _p.c.supervision                             == 1, 
            cast(_p.c.typeextenumbersright,VARCHAR(255)) ==	cast(_e.c.type,VARCHAR(255)), # 'user'
            _p.c.typevalextenumbersright                 == cast(_l2.c.iduserfeatures,VARCHAR(255)),
            _e.c.typeval                                 == cast(_l2.c.id,VARCHAR(255)),
            coalesce(_l.c.number,'')                     != ''
        ]
        if 'context' in kwargs:
            conds.append(_l.c.context == kwargs['context'])

        q = select([_e.c.exten, _l.c.number],	and_(*conds))

        return self.execute(q).fetchall()


class ProgfunckeysHintsHandler(SpecializedHandler):
    def all(self, *args, **kwargs):
        (_u, _p, _e, _l) = [getattr(self.db, o)._table for o in
                ('userfeatures','phonefunckey','extenumbers','linefeatures')]

        conds = [
                _l.c.iduserfeatures      == _p.c.iduserfeatures, 
                _p.c.typeextenumbers     != None,
                _p.c.typevalextenumbers  != None,
                _p.c.supervision         == 1, 
                _p.c.progfunckey         == 1,
                cast(_p.c.typeextenumbers,VARCHAR(255)) == cast(_e.c.type,VARCHAR(255)),
                _p.c.typevalextenumbers  != 'user',
                _p.c.typevalextenumbers  == _e.c.typeval
        ]
        if 'context' in kwargs:
            conds.append(_l.c.context == kwargs['context'])

        q = select(
            [_p.c.iduserfeatures, _p.c.exten, _p.c.typeextenumbers,
             _p.c.typevalextenumbers, _p.c.typeextenumbersright,
             _p.c.typevalextenumbersright, _e.c.exten.label('leftexten')],

            and_(*conds)
        )

        """
        _l2 = alias(_l)

        conds = [
                _l.c.iduserfeatures      == _p.c.iduserfeatures, 
                _p.c.typeextenumbers     != None,
                _p.c.typevalextenumbers  != None,
                _p.c.supervision         == 1, 
                _p.c.progfunckey         == 1,
                cast(_p.c.typeextenumbers,VARCHAR(255)) == cast(_e.c.type,VARCHAR(255)),
                _p.c.typevalextenumbers  == 'user',
                _p.c.typevalextenumbers  == cast(_l2.c.iduserfeatures,VARCHAR(255)),
                _e.c.typeval             == cast(_l2.c.id,VARCHAR(255))
        ]
        if 'context' in kwargs:
            conds.append(_l.c.context == kwargs['context'])

        q2 = select(
            [_p.c.iduserfeatures, _p.c.exten, _p.c.typeextenumbers,
             _p.c.typevalextenumbers, _p.c.typeextenumbersright,
             _p.c.typevalextenumbersright, _e.c.exten.label('leftexten')],

            and_(*conds)
        )

        return self.execute(q1.union(q2)).fetchall()
        """
        return self.execute(q).fetchall()


class PickupsHandler(SpecializedHandler):
    """

        NOTE: all user lines can be intercepted/intercept calls
    """
    def all(self, usertype, *args, **kwargs):
        if usertype not in ('sip','iax','sccp'):
            raise TypeError

        (_p, _pm, _lf, _u, _g, _q, _qm) = [getattr(self.db, o)._table.c for o in
                ('pickup','pickupmember','linefeatures','user'+usertype, 'groupfeatures',
                'queuefeatures', 'queuemember')]

        # simple users
        q1 = select([_u.name, _pm.category, _p.id],
            and_(
                _p.commented    == 0,
                _p.id           == _pm.pickupid,
                _pm.membertype  == 'user',
                _pm.memberid    == _lf.iduserfeatures,
                #_lf.line_num    == 0,
                #_lf.rules_order == 0,
                _lf.protocol    == usertype,
                _lf.protocolid  == _u.id
            )
        )

        # groups
        q2 = select([_u.name, _pm.category, _p.id],
            and_(
                _p.commented    == 0,
                _p.id           == _pm.pickupid,
                _pm.membertype  == 'group',
                _pm.memberid    == _g.id,
                _g.name         == _qm.queue_name,
                _qm.usertype    == 'user',
                _qm.userid      == _lf.iduserfeatures,
                #_lf.line_num    == 0,
                #_lf.rules_order == 0,
                _lf.protocol    == usertype,
                _lf.protocolid  == _u.id
            )
        )

        # queues
        q3 = select([_u.name, _pm.category, _p.id],
            and_(
                _p.commented    == 0,
                _p.id           == _pm.pickupid,
                _pm.membertype  == 'queue',
                _pm.memberid    == _q.id,
                _q.name         == _qm.queue_name,
                _qm.usertype    == 'user',
                _qm.userid      == _lf.iduserfeatures,
                #_lf.line_num    == 0,
                #_lf.rules_order == 0,
                _lf.protocol    == usertype,
                _lf.protocolid  == _u.id
            )
        )

        return self.execute(q1.union(q2.union(q3))).fetchall()

class QueuePenaltiesHandler(SpecializedHandler):
    def all(self, **kwargs):
        (_p, _pc) = [getattr(self.db, o)._table.c for o in ('queuepenalty','queuepenaltychange')]

        q = select(
                [_p.name, _pc.seconds, _pc.maxp_sign, _pc.maxp_value, _pc.minp_sign, _pc.minp_value],
                and_(
                    _p.commented == 0,
                    _p.id        == _pc.queuepenalty_id
                )
        ).order_by(_p.name)

        return self.execute(q).fetchall()

class TrunksHandler(SpecializedHandler):
    def all(self, **kwargs):
        (_t, _s, _i) = [getattr(self.db,o)._table.c for o in ('trunkfeatures','usersip','useriax')]

        q1 = select([_t.id, _t.protocol, _s.username, _s.secret, _s.host],
            and_(
                _t.protocol   == 'sip',
                _t.protocolid == _s.id,
                _s.commented  == 0,
            )
        )
        q2 = select([_t.id, _t.protocol, _i.username, _i.secret, _i.host],
            and_(
                _t.protocol   == 'iax',
                _t.protocolid == _i.id,
                _i.commented  == 0,
            )
        )
        return self.execute(q2.union(q1)).fetchall()
    #return self.execute(q1).fetchall()

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

        'trunks'        : TrunksHandler,
        'siptrunks'     : ('usersip', {'category': 'trunk'}),
        'iaxtrunks'     : ('useriax', {'category': 'trunk'}),

        'voicemails'    : ('voicemail',),
        'queues'        : ('queue',),
        'queuemembers'  : ('queuemember',),
        'queuepenalty'  : ('queuepenalty',),

        'userqueueskills': UserQueueskillsHandler,
        'agentqueueskills': AgentQueueskillsHandler,
        'queueskillrules': ('queueskillrule',),
        'extensions'    : ('extensions',),
        'contexts'      : ('context',),
        'contextincludes': ('contextinclude',),

        'extenumbers'   : ExtenumbersHandler,
        'voicemenus'    : ('voicemenu',),
        'hints'         : HintsHandler,
        'phonefunckeys' : PhonefunckeysHandler,
        'bsfilterhints' : BSFilterHintsHandler,
        'progfunckeys'  : ProgfunckeysHintsHandler,

        'pickups'       : PickupsHandler,
        'queuepenalties': QueuePenaltiesHandler,
        'parkinglot'    : ('parkinglot',),
        'dundi'         : ('dundi',),
        'dundimapping'  : ('dundi_mapping',),
        'dundipeer'     : ('dundi_peer',),
        'general'       : ('general',),
        'dahdi'         : ('dahdi_general',),
        'dahdigroup'    : ('dahdi_group',),
    }

    def __init__(self, db, name):
        self.db   = db
        self.name = name

    @iterable('list')
    def all(self, commented=None, order=None, asc=True, **kwargs):
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
            if not asc:
                order = desc(order)
            q = q.order_by(order)

        return q.all()

    @iterable('single')
    def get(self, **kwargs):
        q = getattr(self.db, self._translation.get(self.name, (self.name,))[0])

        conds = []
        for k, v in kwargs.iteritems():
            conds.append(getattr(q,k) == v)
        return q.filter(and_(*conds)).first()


class XivoDBBackend(Backend):
    def __init__(self, uri):
        sqlalchemy.convert_unicode = True
        self.db = SqlSoup(uri,
                session=scoped_session(sessionmaker(autoflush=True,expire_on_commit=False,autocommit=True)))

    def __getattr__(self, name):
        if not name in QObject._translation:
            raise KeyError(name)

        if inspect.isclass(QObject._translation[name]) and\
             issubclass(QObject._translation[name], SpecializedHandler):
            return QObject._translation[name](self.db, name)

        return QObject(self.db, name)

