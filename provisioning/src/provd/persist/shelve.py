# -*- coding: UTF-8 -*-

# next line is to prevent from importing our own module when doing 'import shelve'
from __future__ import absolute_import

__license__ = """
    Copyright (C) 2011  Avencall

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

import logging
import os
import shelve
from provd.persist.id import get_id_generator_factory
from provd.persist.util import new_backend_based_collection

logger = logging.getLogger(__name__)


def _convert_to_backend(id):
    # Pre: id is a unicode string
    return id.encode('UTF-8')


class ShelveSimpleBackend(object):
    # in python 2, shelve doesn't accept unicode string as keys, that's why
    # this layer is needed

    def __init__(self, filename):
        self._shelve = shelve.open(filename)
        self._closed = False

    def close(self):
        try:
            self._shelve.close()
        except Exception, e:
            logger.error('Error while closing shelve: %s', e)
            raise
        else:
            self._closed = True

    def __getitem__(self, id):
        real_id = _convert_to_backend(id)
        return self._shelve[real_id]

    def __setitem__(self, id, document):
        real_id = _convert_to_backend(id)
        self._shelve[real_id] = document

    def __delitem__(self, id):
        real_id = _convert_to_backend(id)
        del self._shelve[real_id]

    def __contains__(self, id):
        real_id = _convert_to_backend(id)
        return real_id in self._shelve

    def itervalues(self):
        return self._shelve.itervalues()


def new_shelve_collection(filename, generator):
    return new_backend_based_collection(ShelveSimpleBackend(filename),
                                        generator)


class ShelveDatabase(object):
    def __init__(self, shelve_dir, generator_factory):
        self._shelve_dir = shelve_dir
        self._generator_factory = generator_factory
        self._collections = {}
        self._create_shelve_dir()

    def _create_shelve_dir(self):
        if not os.path.isdir(self._shelve_dir):
            os.makedirs(self._shelve_dir)

    def close(self):
        for collection in self._collections.itervalues():
            collection.close()
        self._collections = {}

    def _new_collection(self, id):
        generator = self._generator_factory()
        filename = os.path.join(self._shelve_dir, id)
        try:
            return new_shelve_collection(filename, generator)
        except Exception, e:
            # could not create collection
            raise ValueError(e)

    def collection(self, id):
        if id not in self._collections or self._collections[id]._closed:
            self._collections[id] = self._new_collection(id)
        return self._collections[id]


class ShelveDatabaseFactory(object):
    def new_database(self, type, generator, **kwargs):
        if type != 'shelve':
            raise ValueError('unrecognised type "%s"' % type)
        try:
            shelve_dir = kwargs['shelve_db_dir']
        except KeyError:
            raise ValueError('missing "shelve_db_dir" arguments in "%s"' % kwargs)
        else:
            generator_factory = get_id_generator_factory(generator)
            return ShelveDatabase(shelve_dir, generator_factory)
