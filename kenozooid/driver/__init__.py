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
Support for dive computers, dive data loggers and other measurment devices
used in diving.

The module specifies set of interfaces to be implemented by device drivers.
"""

import logging

import kenozooid.component as kc

log = logging.getLogger('kenozooid.driver')

class DeviceDriver(object):
    """
    Device driver interface.

    Every device driver implementation has to implement at least this
    interface.

    Software using this interface shall get driver instance using
    `DeviceDriver.scan` method.

    There is only one known method for platform independent device scanning
    and it applies to USB devices only. Library pyUSB can be used to find
    devices, i.e.::

        import usb.core
        dev = usb.core.find(idVendor=0x0403, idProduct=0x6001)
        dev.write(...)
        dev.read(...)

    Above code uses not released yet pyUSB 1.0 interfaces. Device's `write`
    and `read' methods can be used to communicate with a device. It is not yet
    possible to determine port of a device (i.e. /dev/ttyUSB0, COM1, etc.),
    so it is not possible to bind this method with pySerial usage when
    required.
    """
    @staticmethod
    def scan(port=None):
        """
        Scan for connected devices and return device driver instances.

        Each connected dive computer should get one device driver instance.

        If port is specified, then a driver instance should be returned,
        which connects to the port.
        """

    def version(self):
        """
        Get model and firmware version information about connected dive
        computer.
        """


class Simulator(object):
    """
    Diving computer dive simulation interface.
    """
    driver = None

    def start(self):
        """
        Start dive simulation on dive computer.
        """
        pass


    def stop(self):
        """
        Stop dive simulation on dive computer.
        """
        pass


    def depth(self, d):
        """
        Send simulated depth to a dive computer.
        """
        pass



class DataParser(object):
    """
    Diving computer data parser interface.

    Depending on dive computer firmware capabilities, driver implementing
    the interface shall dump all possible data from dive computer like

    - dive computer settings
    - all entries from dive logbook
    - battery information
    """
    driver = None

    def dump(self):
        """
        Get raw data from dive computer.
        """

    def dives(self, data):
        """
        Parse dive data from raw data.
        
        Iterator of dives is returned.

        :Parameters:
         data
            Raw dive computer data.
        """


    def gases(self, data):
        """
        Get list of gases per dive.

        Iterator of tuples of gases is returned. A tuple of gases is list
        of gases used during a dive.

        :Parameters:
         data
            Raw dive computer data.
        """


    def version(self, data):
        """
        Extract model and version information from dive computer raw data.

        :Parameters:
         data
            Raw dive computer data.
        """


class DeviceError(BaseException):
    """
    Device communication error.
    """


def find_driver(iface, query, port=None):
    """
    Find device driver implementing an interface.

    Query parameter is used to find driver by its id or device model.
    Device error exception is raised if driver is not found.

    If device driver does not support functionality specified by an
    interface, then None is returned.

    :Parameters:
     iface
        Interface of functionality.
     query
        Device driver id or device model string.
     port
        Device port (i.e. /dev/ttyUSB0, COM1).
    """
    found = False
    for cls in kc.query(DeviceDriver):
        p = kc.params(cls)
        id = p['id']
        models = p['models']
        if id == query or any(query.startswith(m) for m in models):
            found = True
            log.debug('found device driver for query: {0}'.format(query))
            break

    if not found:
        raise DeviceError('Device driver not found, query: {0}'.format(query))

    # scan for connected devices
    try:
        drv = next(cls.scan(port))
    except StopIteration as ex:
        raise DeviceError('Driver "{}" cannot communicate with a device at'
                ' port "{}"'.format(id, port))

    # find class implementing specified interface (and functionality)
    try:
        cls = next(kc.query(iface, id=id))
        obj = cls()
        obj.driver = drv
        return obj
    except StopIteration as ex:
        return None


# vim: sw=4:et:ai
