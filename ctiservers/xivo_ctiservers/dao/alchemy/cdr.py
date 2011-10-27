# -*- coding: UTF-8 -*-

from sqlalchemy import text
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String
from xivo_ctiservers.dao.alchemy.base import Base


class CDR(Base):
    __tablename__ = 'cdr'

    id = Column(Integer, primary_key=True)
    calldate = Column(DateTime)
    clid = Column(String(80, convert_unicode=True),
            nullable=False, server_default=u'')
    src = Column(String(80, convert_unicode=True),
            nullable=False, server_default=u'')
    dst = Column(String(80, convert_unicode=True),
            nullable=False, server_default=u'')
    dcontext = Column(String(39, convert_unicode=True),
            nullable=False, server_default=u'')
    channel = Column(String(80, convert_unicode=True),
            nullable=False, server_default=u'')
    dstchannel = Column(String(80, convert_unicode=True),
            nullable=False, server_default=u'')
    lastapp = Column(String(80), nullable=False, server_default='')
    lastdata = Column(String(80), nullable=False, server_default='')
    answer = Column(DateTime)
    end = Column(DateTime)
    duration = Column(Integer, nullable=False, server_default=text('0'))
    billsec = Column(Integer, nullable=False, server_default=text('0'))
    disposition = Column(String(9), nullable=False, server_default='')
    amaflags = Column(Integer, nullable=False, server_default=text('0'))
    accountcode = Column(String(20), nullable=False, server_default='')
    uniqueid = Column(String(32), nullable=False, server_default='')
    userfield = Column(String(255), nullable=False, server_default='')
