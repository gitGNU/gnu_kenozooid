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
Test command line routines.
"""

import unittest

from kenozooid.cli.uddf import parse_range, RangeError


class RangeTestCase(unittest.TestCase):
    """
    Numerical range tests.
    """
    def test_simple(self):
        """Test parsing simple numerical ranges
        """
        self.assertEquals((1, 2, 3), parse_range('1-3'))
        self.assertEquals((2, 4), parse_range('2,4'))
        self.assertEquals((1, 3, 4, 5, 6, 7), parse_range('1,3,4-7'))


    def test_inifinity(self):
        """Test parsing infinite numerical ranges
        """
        self.assertEquals(tuple(range(30, 101)), parse_range('30-'))
        self.assertEquals(tuple(range(900, 1001)),
                parse_range('900-', infinity=1000))


    def test_errors(self):
        """Test invalid ranges
        """
        self.assertRaises(RangeError, parse_range, '30--')
        self.assertRaises(RangeError, parse_range, '30-2-')
        self.assertRaises(RangeError, parse_range, '1,a,2')
        self.assertRaises(RangeError, parse_range, '1-a,3')

