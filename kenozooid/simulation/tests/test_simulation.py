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

import unittest

from kenozooid.simulation import parse

class SpecParserTestCase(unittest.TestCase):
    def test_single_sec(self):
        """Test parsing single value with seconds
        """
        result = tuple(parse('14,5'))
        self.assertEquals(((14, 5),), result)


    def test_multiple_sec(self):
        """Test parsing multiple values with seconds
        """
        result = tuple(parse('14,5  15,8'))
        self.assertEquals(((14, 5), (15, 8)), result)


    def test_minutes(self):
        """Test parsing values with minutes
        """
        result = tuple(parse('0:14,5  5:15,8'))
        self.assertEquals(((14, 5), (315, 8)), result)


    def test_invalid_time(self):
        """Test parsing when invalid time specified
        """
        try:
            tuple(parse('0:14,5  5-15,8'))
        except ValueError, ex:
            self.assertTrue('Invalid time specification' in str(ex))


    def test_invalid_depth(self):
        """Test parsing when invalid depth specified
        """
        try:
            tuple(parse('0:14,5  5:15,'))
        except ValueError, ex:
            self.assertTrue('Invalid depth specification' in str(ex))

