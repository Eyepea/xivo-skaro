# -*- coding: UTF-8 -*-

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

import json
import logging
import os
from copy import deepcopy
from provd.persist.id import get_id_generator_factory
from provd.persist.util import new_backend_based_collection

logger = logging.getLogger(__name__)


class JsonSimpleBackend(object):
    closed = False

    def __init__(self, directory):
        self._directory = directory
        self._dict = {}
        self._load()
        self._closed = False

    def _load(self):
        if not os.path.isdir(self._directory):
            os.mkdir(self._directory)

        for rel_filename in os.listdir(self._directory):
            abs_filename = os.path.join(self._directory, rel_filename)
            try:
                fobj = open(abs_filename)
            except EnvironmentError, e:
                logger.warning('Could not open file %s: %s', abs_filename, e)
            else:
                try:
                    document = json.load(fobj)
                except ValueError:
                    logger.warning('Could not decode JSON document %s: %s', abs_filename, e)
                else:
                    self._dict[rel_filename.decode('ascii')] = document
                finally:
                    fobj.close()

    def close(self):
        self._dict = {}
        self._closed = True

    def __getitem__(self, id):
        return deepcopy(self._dict[id])

    def __setitem__(self, id, document):
        self._dict[id] = deepcopy(document)
        abs_filename = os.path.join(self._directory, id.encode('ascii'))
        fobj = open(abs_filename, 'w')
        try:
            json.dump(document, fobj, separators=(',', ':'))
        finally:
            fobj.close()

    def __delitem__(self, id):
        del self._dict[id]
        abs_filename = os.path.join(self._directory, id.encode('ascii'))
        try:
            os.remove(abs_filename)
        except EnvironmentError, e:
            logger.info('Error while removing JSON document %s: %s', e)

    def __contains__(self, id):
        return id in self._dict

    def itervalues(self):
        for document in self._dict.itervalues():
            yield deepcopy(document)


def new_json_collection(directory, generator):
    return new_backend_based_collection(JsonSimpleBackend(directory),
                                        generator)


class JsonDatabase(object):
    def __init__(self, base_directory, generator_factory):
        self._base_directory = base_directory
        self._generator_factory = generator_factory
        self._collections = {}
        self._create_base_directory()

    def _create_base_directory(self):
        if not os.path.isdir(self._base_directory):
            os.makedirs(self._base_directory)

    def close(self):
        for collection in self._collections.itervalues():
            collection.close()
        self._collections = {}

    def _new_collection(self, id):
        generator = self._generator_factory()
        directory = os.path.join(self._base_directory, id)
        try:
            return new_json_collection(directory, generator)
        except Exception, e:
            # could not create collection
            raise ValueError(e)

    def collection(self, id):
        if id not in self._collections or self._collections[id]._closed:
            self._collections[id] = self._new_collection(id)
        return self._collections[id]


class JsonDatabaseFactory(object):
    def new_database(self, type, generator, **kwargs):
        if type != 'json':
            raise ValueError('unrecognised type "%s"' % type)
        try:
            base_directory = kwargs['json_db_dir']
        except KeyError:
            raise ValueError('missing "json_db_dir" arguments in "%s"' % kwargs)
        else:
            generator_factory = get_id_generator_factory(generator)
            return JsonDatabase(base_directory, generator_factory)
