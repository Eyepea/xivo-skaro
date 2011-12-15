# -*- coding: UTF-8 -*-

"""Localization service.

A localization service holds the current locale and make it possible to
register callbacks with it so to be warned when the locale changes.

The word localization is used although that, at the time of writing this,
there's only basic support for multiple languages and not really any other
localization related things.

Valid locales are in the format language[_territory], i.e. 'fr' and 'fr_CA'
for example. We do not support the full POSIX locale identifiers (with codeset
and modifiers) as for now since there would be no use.

"""

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
import re
import weakref

logger = logging.getLogger(__name__)

_L10N_SERVICE = None
_LOCALE_REGEX = re.compile(r'^[a-z]{2,3}(?:_[A-Z]{2,3})?$')

# List of events
LOCALE_CHANGED = 'locale_changed'


class LocalizationService(object):
    def __init__(self, locale=None):
        self._locale = locale
        self._observers = weakref.WeakKeyDictionary()

    def attach_observer(self, observer):
        """Attach an observer to this localization service.
        
        Note that since observers are weakly referenced, you MUST keep a
        reference to each one somewhere in the application if you want them
        not to be immediately garbage collected.
        
        An observer is a callable object taking a tuple (<event>, arg).
        
        """
        logger.debug('Attaching localization observer %s', observer)
        if observer in self._observers:
            logger.info('Observer %s was already attached', observer)
        else:
            self._observers[observer] = None

    def detach_observer(self, observer):
        logger.debug('Detaching localization observer %s', observer)
        try:
            del self._observers[observer]
        except KeyError:
            logger.info('Observer %s was not attached', observer)

    def _notify(self, event, arg):
        logger.debug('Notifying localization observers: %s %s', event, arg)
        for observer in self._observers.keys():
            try:
                logger.info('Notifying localization observer %s', observer)
                observer((event, arg))
            except Exception:
                logger.error('Error while notifying observer %s', observer, exc_info=True)

    def set_locale(self, locale):
        """Set the current locale and fire a LOCALE_CHANGED event if the
        locale has changed.
        
        If locale is None, unset the current locale.
        
        Raise a ValueError if locale is not a valid locale, i.e. is malformed.
        
        """
        if locale is not None and not _LOCALE_REGEX.match(locale):
            raise ValueError('invalid locale %s' % locale)
        if locale != self._locale:
            self._locale = locale
            self._notify(LOCALE_CHANGED, None)

    def get_locale(self):
        """Return the current locale.
        
        If no locale has been set, return None.
        
        """
        return self._locale

    def get_locale_and_language(self):
        """Return a tuple (locale, language) of the current locale."""
        if self._locale is None:
            return None, None
        else:
            return self._locale, self._locale.split('_', 1)[0]


def register_localization_service(l10n_service):
    logger.info('Registering localization service: %s', l10n_service)
    global _L10N_SERVICE
    _L10N_SERVICE = l10n_service


def unregister_localization_service():
    global _L10N_SERVICE
    if _L10N_SERVICE is not None:
        logger.info('Unregistering localization service: %s', _L10N_SERVICE)
        _L10N_SERVICE = None
    else:
        logger.info('No localization service registered')


def get_localization_service():
    """Return the globally registered localization service or None if no
    localization service has been registered.
    
    """
    return _L10N_SERVICE


def get_locale():
    """Return the locale of the globally registered localization service or
    None if no localization service has been registered or no locale has
    been set.
    
    """
    l10n_service = _L10N_SERVICE
    if l10n_service is None:
        return None
    else:
        return l10n_service.get_locale()


def get_locale_and_language():
    """Return the tuple (locale, language) of the globally registered
    localization service or (None, None) if no localization service has been
    registered or no locale has been set.
    
    """
    l10n_service = _L10N_SERVICE
    if l10n_service is None:
        return None
    else:
        return l10n_service.get_locale_and_language()
