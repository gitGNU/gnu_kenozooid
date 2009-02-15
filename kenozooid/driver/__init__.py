#
# Kenozooid - software stack to support different capabilities of dive
# computers.
#
# Copyright (C) 2009 by Artur Wroblewski <wrobell@pld-linux.org>
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

import sys

from kenozooid.component import query

class DeviceDriver(object):
    """
    Device driver interface.

    Every device driver implementation has to implement at least this
    interface.

    Software using this interface shall get driver instance using
    `DeviceDriver.scan` method.
    """
    @staticmethod
    def scan():
        """
        Scan for connected devices and return device driver instances.

        Each connected dive computer should get one device driver instance.
        """

    def version(self):
        """
        Get version information from connected dive computer.
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



class MemoryDump(object):
    """
    Diving computer memory dump interface.

    Depending on dive computer firmware capabilities, driver implementing
    the interface shall dump all possible data from dive computer like

    - dive computer settings
    - all entries from dive logbook
    - battery information
    """
    driver = None

    def dump(self):
        """
        Return iterator of binary data being memory dump.

        Dumped memory will be saved to a file by Kenozooid.
        """

    def convert(self, data, tree):
        """
        Convert dive computer dump data into UDFF format.

        ElementTree parameter is prepared structure of UDDF format. It
        shall be filled with data from memory dump. The structure is saved
        by Kenozooid.

        :Parameters:
         data
            Dive computer memory dump.
         tree
            ElementTree representing UDFF file.
        """


class DeviceError(BaseException):
    """
    Device communication error.
    """


def find_driver(iface, id):
    """
    Find driver implementing an interface.

    :Parameters:
     iface
        Interface of functionality.
     id
        Device driver id.

    If device id is not known or device is not connected, then exception is
    raised.

    If device driver does not support functionality specified by an
    interface, then None is returned.
    """
    # find device driver for device id
    try:
        cls = query(DeviceDriver, id=id).next()
    except StopIteration, ex:
        raise DeviceError('Unknown device driver id %s' % id)

    # scan for connected devices
    try:
        drv = cls.scan().next()
    except StopIteration, ex:
        raise DeviceError('Device with id %s seems to be not connected' % id)

    # find class implementing specified interface (and functionality)
    try:
        cls = query(iface, id=id).next()
        obj = cls()
        obj.driver = drv
        return obj
    except StopIteration, ex:
        return None

