# -*- coding: UTF-8 -*-

"""Standardized service definition and helper."""

__version__ = "$Revision$ $Date$"
__license__ = """
    Copyright (C) 2010-2011  Proformatique <technique@proformatique.com>

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

from zope.interface import Attribute, Interface, implements


class InvalidParameterError(Exception):
    pass


class IConfigureService(Interface):
    """Interface for a simple configuration service.
    
    These services are identified with the string "configure".
    
    These services are similar to key-value store, where you can set a value
    for...
    
    The keys used MUST be strings.
    
    """
    def get(key):
        """Return the value associated with a key.
        
        The object returned might not be a string, but it MUST have the
        following property:
          str_val1 = str(self.get(key))
          self.set(key, str_val1)
          str_val2 = str(self.get(key))
          str_val1 == str_val2
        with str_val1 (and str_val2) being meaningful value for the parameter.
        
        If there's no value associated with key, return None. This means the
        None value can't be associated with a key.
        
        Raise a KeyError if key is not a known valid key. 
        
        """

    def set(key, value):
        """Associate a value with a key.
        
        The object MUST be ready to accept value as a string, although it
        MAY change this value to a different representation. Once this
        value is set, the property of the get method must be respected.
        
        If value is None, this is equivalent to 'deleting' the value. This
        means None has a special meaning and can't be used a value.
        
        Raise an InvalidParameterError if the value for this key is not
        valid/acceptable.
        
        Raise a KeyError if key is not a known valid key.
        
        """
    
    description = Attribute(
        """A dictionary where keys are the key that can be set, and
        values are a short description of the key.
        
        If a parameter has no description, the value for this key MUST be
        None.
        
        """)


class IInstallService(Interface):
    """Interface for an install service.
    
    These services are identified by the string "install".
    
    It offers a download/install/uninstall service, where files can be
    downloaded and manipulated in a way they can be used by the plugin to
    offer extra functionalities.
    
    This service is useful/necessary if some files that a plugin use
    can't be bundled with it because it doesn't have the right to distribute
    these files, or because they are optional and the plugin want to
    let the choice to the user.
    
    """
    def install(pkg_id):
        """Install a package.
        
        The package SHOULD be reinstalled even if it seemed to be installed.
        
        Return an object providing the IProgressOperation interface.
        
        Raise an Exception if there's already an install operation in progress
        for the package.
        
        Raise an Exception if pkg_id is unknown.
        
        """
    
    def uninstall(pkg_id):
        """Uninstall a package.
        
        Raise an Exception if pkg_id is unknown.
        
        """
    
    def list_installable():
        """Return a list of the packages that are installable.
        
        Each item in the list is a dictionary with the following keys:    
          id -- the identifier of the package
        
        The following keys are optional:
          dsize -- the download size of the package, in bytes
          isize -- the installed size of the package, in bytes
        
        """
    
    def list_installed():
        """Return a list of the packages that are installed.
        
        Each item in the list is a dictionary with the following keys:
          id -- the identifier of the package
        
        """


class IUnknownService(Interface):
    """Interface for non-normalized service."""
    
    def do(value):
        """Do something and return a string from a string."""


# Some base service implementation

class IConfigureServiceParam(Interface):
    description = Attribute("The description of this parameter, or None.")
    
    def get():
        """Get the value of this parameter."""
    
    def set(value):
        """Set the value of this parameter.""" 


class AttrConfigureServiceParam(object):
    implements(IConfigureServiceParam)
    
    def __init__(self, object, name, description=None):
        self._obj = object
        self._name = name
        self.description = description
    
    def get(self):
        return getattr(self._obj, self._name)
    
    def set(self, value):
        setattr(self._obj, self._name, value)


class BaseConfigureService(object):
    implements(IConfigureService)
    
    def __init__(self, params_map):
        """
        params_map -- a dictionary object where keys are key and values are
          IConfigureServiceParam object. After a call to this method, the
          params_map object belong to this object. 
        """
        self._params_map = params_map

    def get(self, key):
        param = self._params_map[key]
        return param.get()
    
    def set(self, key, value):
        param = self._params_map[key]
        param.set(value)
    
    @property
    def description(self):
        return dict((key, p.description) for key, p in
                    self._params_map.iteritems())
