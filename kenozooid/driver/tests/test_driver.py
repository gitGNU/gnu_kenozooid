#
# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2012 by Artur Wroblewski <wrobell@pld-linux.org>
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
Basic tests of driver infrastructure.
"""

import unittest

from kenozooid.driver import find_driver, Simulator, DeviceError

import kenozooid.driver.dummy

class DriverFindingTestCase(unittest.TestCase):
    """
    Driver finding tests.
    """
    def test_find(self):
        """Test driver finding
        """
        drv = find_driver(Simulator, 'dummy')
        self.assertTrue(drv is not None)


    def test_not_implemented(self):
        """Test exception on not implemented functionality
        """
        class C: pass # dummy does not implement C interface
        drv = find_driver(C, 'dummy')
        self.assertTrue(drv is None)


    def test_unknown_driver(self):
        """Test exception on unknown driver
        """
        self.assertRaises(DeviceError, find_driver, Simulator, 'unknown')


# vim: sw=4:et:ai
