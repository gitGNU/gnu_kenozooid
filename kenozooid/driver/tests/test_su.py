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
Reefnet Sensus Ultra driver tests.
"""

import unittest
import lxml.objectify as eto

from kenozooid.driver.su import SensusUltraMemoryDump
from kenozooid.uddf import create, validate, q


class SensusUltraUDDFTestCase(unittest.TestCase):
    """
    Sensus Ultra data to UDDF format conversion tests.
    """
    def test_conversion(self):
        """Test basic Sensus Ultra data to UDDF conversion
        """
        dumper = SensusUltraMemoryDump()
        f = open('dumps/su-01.dump')
        tree = create()
        dumper.convert(f, tree)

        # three dives
        self.assertEquals(3, len(tree.findall(q('//dive'))))

        # 247 samples for first dive
        dive = tree.find(q('//dive'))
        data = dive.findall(q('samples/waypoint'))
        self.assertEquals(247, len(data))

        self.assertEquals(2009, dive.date.year)
        self.assertEquals(9, dive.date.month)
        self.assertEquals(20, dive.date.day)
        self.assertEquals(13, dive.time.hour)
        self.assertEquals(10, dive.time.minute)

        eto.deannotate(tree)
        validate(tree)

