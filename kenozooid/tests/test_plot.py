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
Tests of plotting routines.
"""

import unittest
import lxml.objectify as eto
from kenozooid.plot import get_deco

class DecoTestCase(unittest.TestCase):
    """
    Deco related routines tests.
    """
    def test_deco_getting(self):
        """Test getting deco periods.
        """
        wps = eto.XML("""
<samples>
<waypoint><alarm>deco</alarm><divetime>1</divetime><depth>1</depth></waypoint>
<waypoint><alarm>deco</alarm><divetime>1</divetime><depth>1</depth></waypoint>
<waypoint><alarm>deco</alarm><divetime>1</divetime><depth>1</depth></waypoint>
<waypoint></waypoint>
<waypoint><alarm>deco</alarm><divetime>1</divetime><depth>1</depth></waypoint>
<waypoint><alarm>deco</alarm><divetime>1</divetime><depth>1</depth></waypoint>
<waypoint></waypoint>
<waypoint><alarm>deco</alarm><divetime>1</divetime><depth>1</depth></waypoint>
<waypoint><alarm>deco</alarm><divetime>1</divetime><depth>1</depth></waypoint>
<waypoint><alarm>deco</alarm><divetime>1</divetime><depth>1</depth></waypoint>
<waypoint></waypoint>
</samples>
""")
        wps = list(wps.waypoint)
        data = list(get_deco(wps))
        self.assertEquals(3, len(data))
        self.assertEquals(3, len(data[0]))
        self.assertEquals(2, len(data[1]))
        self.assertEquals(3, len(data[2]))

