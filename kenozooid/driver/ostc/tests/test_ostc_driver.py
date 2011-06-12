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
OSTC driver tests.
"""

from collections import namedtuple
from datetime import datetime
import lxml.etree as et
import unittest

import kenozooid.uddf as ku
import kenozooid.driver.ostc.parser as ostc_parser
from kenozooid.driver.ostc import pressure, OSTCMemoryDump

OSTC_DATA = \
   r'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'


class ConversionTestCase(unittest.TestCase):
    """
    Tests of units conversion routines (i.e. depth to pressure).
    """
    def test_pressure_conversion(self):
        """Test depth to pressure conversion
        """
        self.assertEquals(11, pressure(1))
        self.assertEquals(30, pressure(20))
        self.assertEquals(25, pressure(15.5))



class UDDFTestCase(unittest.TestCase):
    """
    OSTC data to UDDF format conversion tests.

    :Attributes:
     dives
        List of dives parsed from OSTC_DATA OSTC data.
    """
    def setUp(self):
        super(UDDFTestCase, self).setUp()
        DCDump = namedtuple('DCDump', 'time data')

        data = ku._dump_decode(OSTC_DATA)
        dump = DCDump(datetime.now(), data)

        dc = OSTCMemoryDump()
        self.dives = list(dc.convert(dump))


    def test_conversion(self):
        """Test basic OSTC data to UDDF conversion
        """
        # five dives
        self.assertEquals(5, len(self.dives))

        # 193 samples for first dive
        dive = self.dives[0]
        data = list(ku.xp(dive, 'uddf:samples/uddf:waypoint'))
        self.assertEquals(195, len(data))

        t = ku.xp_first(dive, 'uddf:datetime/text()')
        self.assertEquals('2009-01-31 23:08:41', t)

        d = ku.xp_first(dive, 'uddf:greatestdepth/text()')
        self.assertEquals('75.0', d)

        d = ku.xp_first(dive, 'uddf:diveduration/text()')
        self.assertEquals('1939', d)

        t = ku.xp_first(dive, 'uddf:lowesttemperature/text()')
        self.assertEquals('300.6', t) # 27.45C


    def test_deco(self):
        """Test OSTC deco data to UDDF conversion
        """
        # get first dive, there are two deco periods
        dive = self.dives[0]
        wps = list(ku.xp(dive, 'uddf:samples/uddf:waypoint'))
        d1 = wps[156:162]
        d2 = wps[168:186]

        # check if all deco waypoints has appropriate alarms
        def alarms(wps):
            return (ku.xp_first(w, 'uddf:alarm/text()') == 'deco' for w in wps)

        t1 = list(alarms(d1))
        t2 = list(alarms(d2))
        self.assertTrue(all(t1), '{0}\n{1}'.format(t1, et.tostring(dive)))
        self.assertTrue(all(t2), '{0}\n{1}'.format(t2, et.tostring(dive)))


# vim: sw=4:et:ai
