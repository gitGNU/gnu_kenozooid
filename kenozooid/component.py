#
# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2011 by Artur Wroblewski <wrobell@pld-linux.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Simple component interface injection and component repository querying
mechanism.
"""

import itertools
import logging

log = logging.getLogger('kenozooid.component')

# component registry
_registry = {}

def inject(iface, **params):
    """
    Class decorator to declare interface implementation.

    Injection parameters can be used to query for classes implementing an
    interface and having appropriate values.

    :Parameters:
     iface
        Interface to inject.
     params
        Injection parameters.
    """
    def f(cls):
        log.debug('inject interface %s for class %s with params %s' \
                % (iface.__name__, cls.__name__, params))

        if iface not in _registry:
            _registry[iface] = []
        _registry[iface].append((cls, params))

        return cls

    return f


def _applies(p1, p2):
    """
    Check if values stored in two dictionaries are equal for all keys
    stored in first dictionary.

    :Parameters:
     p1
        First dictionary.
     p2
        Second dictionary.
    """
    keys = set(p2.keys())
    return all(k in keys and p1[k] == p2[k] for k in p1.keys())


def query(iface=None, **params):
    """
    Look for class implementing specified interface.
    """
    if iface is None:
        data = itertools.chain(*_registry.values())
    elif iface in _registry:
        data = _registry[iface]
    else:
        data = ()

    return (cls for cls, p in data if _applies(params, p))


def params(cls):
    """
    Get interface injection parameters for component realized with
    specified class.

    :Parameters:
     cls
        Class realizing component.
    """
    for c, p in itertools.chain(*_registry.values()):
        if c == cls:
            return p

