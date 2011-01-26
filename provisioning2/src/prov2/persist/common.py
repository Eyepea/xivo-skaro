# -*- coding: UTF-8 -*-

"""Persistent storage interface for 'documents'.

A document is just another term for a dictionary with the following
restrictions:
- must have an 'id' key, which is a unicode string that is unique for
  every document in the same collection.
- every key is a unicode string that match the following regex: [_a-zA-Z0-9]+
- values are either number, boolean, None, unicode string, list or
  dictionaries, and this applies recursively (i.e. you can have a list
  containing dictionaries, etc).

"""

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

# TODO document the syntax/semantic of selector

from zope.interface import Interface

ID_KEY = u'id'


class InvalidIdError(Exception):
    pass


class IDocumentCollection(Interface):
    def close(self):
        """Close the collection."""
    
    def insert(document):
        """Store a new document in the collection and return a deferred that
        will fire with the ID of the newly added document once the document
        has been successfully inserted.
        
        If document has an 'id' key, it is used as the ID. Else, an ID is
        generated and added to the document (the document object passed in
        will be modified). The deferred errback is fired with an
        InvalidIdError if the given ID is already in used. This mean that
        when the deferred fire it's callback, document is guaranteed to have
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
        
        The deferred will fire its errback with an InvalidIdError if there'S
        no document with the given ID.
        
        """
    
    def retrieve(id):
        """Return a deferred that will fire with the document with the given
        ID, or fire with None if there's no such document.
        
        """
        
    def find(selector):
        """Return a deferred that will fire with an iterator over documents
        that match the selector.
        
        A selector is a dictionary with some special semantic.
        
        Note that you can iterate over all the documents by passing an
        empty selector ({}).
        
        """
    
    def find_one(selector):
        """Return a deferred that will fire with the 'first' document that
        match the selector, or fire with None if there's no document. 
        
        """
