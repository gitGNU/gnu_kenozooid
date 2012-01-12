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

import unittest

from kenozooid.simulation import parse, interpolate

class SpecParserTestCase(unittest.TestCase):
    """
    Parser of specification of dive simulation tests.
    """
    def test_single_sec(self):
        """
        Test parsing single value with seconds
        """
        result = tuple(parse('14,5'))
        self.assertEquals(((14, 5),), result)


    def test_multiple_sec(self):
        """
        Test parsing multiple values with seconds
        """
        result = tuple(parse('14,5  15,8'))
        self.assertEquals(((14, 5), (15, 8)), result)


    def test_minutes(self):
        """
        Test parsing values with minutes
        """
        result = tuple(parse('0:14,5  5:15,8'))
        self.assertEquals(((14, 5), (315, 8)), result)


    def test_invalid_time(self):
        """
        Test parsing when invalid time specified
        """
        try:
            tuple(parse('0:14,5  5-15,8'))
        except ValueError as ex:
            self.assertTrue('Invalid runtime specification' in str(ex))


    def test_invalid_depth(self):
        """
        Test parsing when invalid depth specified
        """
        try:
            tuple(parse('0:14,5  5:15,'))
        except ValueError as ex:
            self.assertTrue('Invalid depth specification' in str(ex))



class InterpolationTestCase(unittest.TestCase):
    """
    Dive simulation times and depths interpolation tests.
    """
    def test_descent(self):
        """
        Test descent interpolation
        """
        spec = ((1, 1), (2, 2))
        result = interpolate(spec)
        self.assertEquals(((0, 0), (1, 1), (2, 2)), tuple(result))

        spec = ((1, 1), (4, 4))
        result = interpolate(spec)
        self.assertEquals(((0, 0), (1, 1), (2, 2), (3, 3), (4, 4)), tuple(result))

        spec = ((2, 10),)
        result = interpolate(spec)
        self.assertEquals(((0, 0), (1, 5), (2, 10)), tuple(result))

        spec = ((2, 10), (15, 30))
        result = interpolate(spec)
        result = tuple(result)
        self.assertEquals((0, 0), result[0])
        self.assertEquals((3, 11), result[3])
        self.assertEquals((4, 13), result[4])
        self.assertEquals((13, 26), result[-3])
        self.assertEquals((14, 28), result[-2])
        self.assertEquals((15, 30), result[-1])


    def test_ascent(self):
        """
        Test ascent interpolation
        """
        spec = ((2, 10), (4, 5))
        result = interpolate(spec)
        result = tuple(result)[3:]
        self.assertEquals(((3, 7), (4, 5)), result)

        spec = ((3, 15), (15, 10))
        result = tuple(interpolate(spec))[3:]
        self.assertEquals((3, 15), result[0])
        self.assertEquals((5, 14), result[1])
        self.assertEquals((12, 11), result[-2])
        self.assertEquals((15, 10), result[-1])


    def test_no_depth_change(self):
        """
        Test no depth change interpolation
        """
        spec = ((1, 15), (5, 15))
        result = interpolate(spec)
        self.assertEquals(((0, 0), (1, 15), (5, 15)), tuple(result))


    def test_slow_descent(self):
        """
        Test slow descent interpolation
        """
        spec = ((4, 1),)
        result = interpolate(spec)
        self.assertEquals(((0, 0), (4, 1)), tuple(result))

        spec = ((6, 2),)
        result = interpolate(spec)
        self.assertEquals(((0, 0), (3, 1), (6, 2)), tuple(result))

        spec = ((6, 3),)
        result = interpolate(spec)
        self.assertEquals(((0, 0), (2, 1), (4, 2), (6, 3)), tuple(result))


    def test_slow_ascent(self):
        """
        Test slow ascent interpolation
        """
        spec = ((4, 1), (5, 0))
        result = interpolate(spec)
        self.assertEquals(((0, 0), (4, 1), (5, 0)), tuple(result))

        spec = ((6, 2), (10, 4))
        result = interpolate(spec)
        result = tuple(result)[2:]
        self.assertEquals(((6, 2), (8, 3), (10, 4)), result)

        spec = ((6, 2), (12, 4))
        result = interpolate(spec)
        result = tuple(result)[2:]
        self.assertEquals(((6, 2), (9, 3), (12, 4)), result)


