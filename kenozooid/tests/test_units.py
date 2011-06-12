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

import unittest

from kenozooid.units import C2K

class TemperatureTestCase(unittest.TestCase):
    def test_c2k(self):
        """Test Celsius to Kelvin conversion
        """
        self.assertAlmostEquals(294.15, C2K(21), 3)
        self.assertAlmostEquals(282.05, C2K(8.9), 3)


    def test_k2c(self):
        """Test Kelvin to Celsius conversion
        """
        self.assertAlmostEquals(C2K(21), 294.15, 3)
        self.assertAlmostEquals(C2K(8.9), 282.05, 3)

