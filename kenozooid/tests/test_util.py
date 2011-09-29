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
Tests for Kenozooid utility functions.
"""

import unittest

from kenozooid.util import nformat, pipe, nit

class PipeDataTestCase(unittest.TestCase):
    """
    Data piping tests.
    """
    def test_pipe(self):
        """
        Test data piping
        """
        f1 = lambda it: (i + 1 for i in it)
        f2 = lambda it: (i * 2 for i in it)
        self.assertEquals([2, 4, 6, 8], list(pipe(range(4), f1, f2)))


    def test_pipe_order(self):
        """
        Test order of data piping
        """
        f1 = lambda it: (i + 1 for i in it)
        f2 = lambda it: (i * 2 for i in it)
        self.assertEquals([2, 4, 6, 8], list(pipe(range(4), f1, f2)))
        self.assertEquals([1, 3, 5, 7], list(pipe(range(4), f2, f1)))


class UtilsTestCase(unittest.TestCase):
    """
    Tests for various utils.
    """
    def test_nit(self):
        """
        Test nit
        """
        it = (1, 2, 3, 4)
        self.assertEquals(it, nit(it))

        v = nit(None)
        self.assertEquals(list(), list(v))


    def test_format(self):
        """
        Test None value formatting
        """
        self.assertEquals('test ', nformat('{0} {1}', 'test', None))
        self.assertEquals('', nformat('{0}', None))


# vim: sw=4:et:ai
