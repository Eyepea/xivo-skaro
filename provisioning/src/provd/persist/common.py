# -*- coding: UTF-8 -*-

"""Persistent storage interface for 'documents'.

A document is just another term for a dictionary with the following
restrictions:
- must have an 'id' key, which is a unicode string matching \w+ that is unique
  for every document in the same collection.
- every key is a unicode string that match the following regex: [_a-zA-Z0-9]+
- values are either number, boolean, None, unicode string, list or
  dictionaries, and this applies recursively (i.e. you can have a list
  containing dictionaries, etc).

Some operations take a "selector" in arguments. A selector is a dictionary
with some special semantic. It is inspired from the query language of mongodb.

Here's examples of valid selector and the documents the selector will match:
- {}
    match every docs
- {"a": 1}
    docs where "a" is 1 or an array containing 1
    Match: {"a": 1}, {"a": [1]}, {"a": [1, 2]}, {"a": 1, "b": 2}
    Not match: {"a": "1"}, {}
- {"a": 1, "b": 2}
    docs where "a" is 1 or an array containing 1 and b is 2 or an array
    containing 2
    Match: {"a": 1, "b": 2}, {"a": 1, "b": 2, "c": 3}
    Not match: {"a": 1}
- {"a": [1]}
    docs where "a" is the array [1]
    Match: {"a": [1]}, {"a": [1], "b": 2}
    Not match: {"a": 1}, {"a": [1, 2]}
- {"a": {"b": 2}}
    docs where "a" is the dictionary {"b": 2}
    Match: {"a": {"b": 2}}, {"a": {"b": 2}, "c": 3}
    Not match: {"a": {"b": 2, "c": 3}}, {"a": {"b": [2]}},
- {"a.b": 2}
    docs where "a" is a dictionary for which "b" is 2 or an array containing 2
    Match: {"a": {"b": 2}}, {"a": {"b": [2]}}, {"a": {"b": 2, "c": 3}}
- {"a": {"$in": [1, 2]}}
    docs where "a" is either 1 or 2 or an array containing either 1 or 2
    Match: {"a": 1}, {"a": 2}, {"a": [1]}, {"a": [1, 3]}

"""

__version__ = "$Revision$ $Date$"
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

from zope.interface import Interface

ID_KEY = u'id'


class InvalidIdError(Exception):
    pass


class IDocumentCollection(Interface):
    """A collection of documents."""
    
    def close():
        """Close the collection. This method may be called more than once, and
        if it doesn't raise an exception on the first time, it should not
        raise an exception the next times it is called.
        
        """
    
    def insert(document):
        """Store a new document in the collection and return a deferred that
        will fire with the ID of the newly added document once the document
        has been successfully inserted.
        
        If document has an 'id' key, it is used as the ID. Else, an ID is
        generated and added to the document (the document object passed in
        will be modified). The deferred errback is fired with an
        InvalidIdError if the given ID is already in used. This mean that
        when the deferred fire its callback, document is guaranteed to have
        an 'id' key.
        
        """
    
    def update(document):
        """Update the document with the current document and return a
        deferred that fire with None once the document has been successfully
        updated.
        
        The document must have an 'id' key that is a valid ID in the
        collection, else the deferred will fire its errback with an
        InvalidIdError.
        
        """
    
    def delete(id):
        """Delete the document with the given ID and return a deferred that
        fire with None once the document with the given id has been
        successfully deleted.
        
        The deferred will fire its errback with an InvalidIdError if there's
        no document with the given ID.
        
        """
    
    def retrieve(id):
        """Return a deferred that will fire with the document with the given
        ID, or fire with None if there's no such document.
        
        """
    
    def find(selector, fields, skip, limit, sort):
        """Return a deferred that will fire with an iterator over documents
        that match the selector.
        
        Valid arguments to this method are, in order:
          selector -- a selector (i.e. a dict)
          fields -- a list of fields to include for every matched documents.
            Note that the id fields is always included. If not specified
            or empty, return all the fields
          skip -- a skip value, i.e. the number of documents to skip. If not
            specified or 0, no matching documents are skipped.
          limit -- a limit, i.e. the maximum number of documents to return. If
            not specified or 0, all matching documents are returned.
          sort -- a tuple (key, direction), where key is the key to do the sort
            and direction is either 1 for ASC and -1 for DESC. If not specified,
            the matching documents are not sorted.
        
        All arguments are optional except for selector.
        
        """
    
    def find_one(selector):
        """Return a deferred that will fire with the 'first' document that
        match the selector, or fire with None if there's no document. 
        
        """
    
    def ensure_index(complex_key):
        """Create an index on the given complex key if it does not already
        exist and return a deferred that fire with None once the index has
        been created.
        
        complex_key has the same format as keys for selectors, i.e. it
        can be of the form 'a.b' for example.
        
        This is an optional operation, and some implementation might not
        implement it, i.e. you should be ready to catch an AttributeError
        when accessing the 'ensure_index' name.
        
        """


class IDatabase(Interface):
    """A database is a group of zero or more document collections."""
    
    def close():
        """Close the underlying collections and the database. All resources
        used by the collections and the database should be freed after a call
        to this method.
        
        """
    
    def collection(id):
        """Return the collection with the given id.
        
        Raise a ValueError if there's no collection with the given id and/or
        it's not possible to create it.
        
        """


class IDatabaseFactory(Interface):
    def new_database(type, generator, **kwargs):
        """Return a new database object.
        
        - type is a string identifying the type of database to create.
        - generator is a string identifying the type of generator to use.   
        
        Raise a ValueError if this factory doesn't recognize type or generator
        as valid values, or if additional arguments are missing or invalid.
        
        """
