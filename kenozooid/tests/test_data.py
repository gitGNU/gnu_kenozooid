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
Tests for Kenozooid data functions.
"""

from datetime import datetime
import unittest

import kenozooid.data as kd

class DivesTestCase(unittest.TestCase):
    """
    Tests for dive sorting, duplicates removal, etc.
    """
    def test_uniq(self):
        """
        Test removal of duplicate removal.
        """
        dives = (kd.Dive(datetime=datetime(2011, 5, 5)),
                kd.Dive(datetime=datetime(2011, 5, 5)),
                kd.Dive(datetime=datetime(2011, 5, 6)))
        ud = list(kd.uniq_dives(dives))
        self.assertEquals(2, len(ud))


# vim: sw=4:et:ai
