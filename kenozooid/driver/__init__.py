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


class DeviceError(BaseException):
    """
    Device communication error.
    """
