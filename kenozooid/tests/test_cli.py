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
Test command line routines.
"""

from kenozooid.cli.logbook import _name_parse

import unittest

class NameParseTestCase(unittest.TestCase):
    """
    Name parsing tests.
    """
    def test_name(self):
        """Test parsing name"""
        f, m, l = _name_parse('Tom Cora')
        self.assertEquals('Tom', f)
        self.assertTrue(m is None)
        self.assertEquals('Cora', l)
            

    def test_name_middle(self):
        """Test parsing name with middle name"""
        f, m, l = _name_parse('Thomas Henry Corra')
        self.assertEquals('Thomas', f)
        self.assertEquals('Henry', m)
        self.assertEquals('Corra', l)


    def test_name_last(self):
        """Test parsing name with lastname first"""
        f, m, l = _name_parse('Corra, Thomas Henry')
        self.assertEquals('Thomas', f)
        self.assertEquals('Henry', m)
        self.assertEquals('Corra', l)


    def test_name_first(self):
        """Test parsing just first name"""
        f, m, l = _name_parse('Tom')
        self.assertEquals('Tom', f)
        self.assertTrue(m is None)
        self.assertTrue(l is None)


# vim: sw=4:et:ai
