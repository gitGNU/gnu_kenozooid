#
# Kenozooid - software stack to support OSTC dive computer.
#
# Copyright (C) 2009 by wrobell <wrobell@pld-linux.org>
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
Set of interfaces to be implemented by dive computers drivers.

Simple interface injection mechanism and searchable registry for classes
implementing given interface are provided.
"""

class DeviceDriver(object):
    def id(self):
        pass


class Simulator(object):
    def start(self):
        pass

    def stop(self):
        pass

    def depth(self, d):
        pass

_registry = {}

def inject(iface, id):
    """
    Class decorator to declare interface implementation.

    Id of driver is required injection attribute. This makes injection
    mechanism very specific to drivers and in the future will be replaced
    by generic paramaters specification, i.e. `inject(iface, **params)`.

    :Parameters:
     iface
        Interface to inject.
     id
        Id of driver.
    """
    def f(cls):
        print 'inject', iface, cls, id

        if iface not in _registry:
            _registry[iface] = {}
        ireg = _registry[iface]
        ireg[id] = cls

        return cls

    return f


def query(iface, id=None):
    """
    Look for class implementing specified interface.
    """
    result = None
    if iface in _registry:
        if id is None:
            result = (cls for _, cls in _registry[iface].items())
        else:
            result = _registry[iface].get(id)

    return tuple(result)


