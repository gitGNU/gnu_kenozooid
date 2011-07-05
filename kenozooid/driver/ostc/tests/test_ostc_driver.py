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

OSTC_MK2_DATA = \
    r'QlpoOTFBWSZTWVJSRrUAO/F/////////////////////////////////////////////4D' \
    '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' \
    'SUka1A=='

RAW_DATA_OSTC = ku._dump_decode(OSTC_DATA)
RAW_DATA_OSTC_MK2 = ku._dump_decode(OSTC_MK2_DATA)

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
        self.dives = list(dc.dives(dump))


    def test_conversion(self):
        """Test basic OSTC data to UDDF conversion
        """
        # five dives
        self.assertEquals(5, len(self.dives))

        # 193 samples for first dive
        dive = self.dives[0]
        data = list(ku.xp(dive, 'uddf:samples/uddf:waypoint'))
        self.assertEquals(195, len(data))

        t = ku.xp_first(dive, 'uddf:informationbeforedive/uddf:datetime/text()')
        self.assertEquals('2009-01-31T23:08:41', t)

        d = ku.xp_first(dive, 'uddf:informationafterdive/uddf:greatestdepth/text()')
        self.assertEquals('75.0', d)

        d = ku.xp_first(dive, 'uddf:informationafterdive/uddf:diveduration/text()')
        self.assertEquals('1939', d)

        t = ku.xp_first(dive, 'uddf:informationafterdive/uddf:lowesttemperature/text()')
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



class MemoryDumpTestCase(unittest.TestCase):
    """
    OSTC memory dump tests.

    :Attributes:
     dump_data
        OSTC raw data from OSTC_DATA.

    """
    def test_version_ostc(self):
        """
        Test OSTC model and version parsing from raw data
        """
        dc = OSTCMemoryDump()
        ver = dc.version(RAW_DATA_OSTC)
        self.assertEquals('OSTC 1.26', ver)


    def test_version_ostc_mk2(self):
        """
        Test OSTC Mk.2 model and version parsing from raw data
        """
        dc = OSTCMemoryDump()
        ver = dc.version(RAW_DATA_OSTC_MK2)
        self.assertEquals('OSTC Mk.2 1.90', ver)



# vim: sw=4:et:ai
