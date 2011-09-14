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

from . import data as od


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
        List of dives parsed from DATA_OSTC.
    """
    def setUp(self):
        super(UDDFTestCase, self).setUp()
        DCDump = namedtuple('DCDump', 'datetime data')

        data = ku._dump_decode(od.DATA_OSTC)
        dump = DCDump(datetime.now(), data)

        dc = OSTCMemoryDump()
        self.dives = list(dc.dives(dump))


    def test_conversion(self):
        """
        Test basic OSTC data to UDDF conversion
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


    def test_deco_alarm(self):
        """
        Test OSTC deco alarm data to UDDF conversion
        """
        dive = self.dives[3] # dive no 3 contains deco alarms
        wps = list(ku.xp(dive, 'uddf:samples/uddf:waypoint'))
        d1 = wps[587:594]
        d2 = wps[743:749]
        d3 = wps[972:976]
        d4 = wps[1320:1343]

        # check if all deco waypoints have appropriate alarms
        def alarms(wps):
            return (ku.xp_first(w, 'uddf:alarm/text()') == 'deco' for w in wps)

        t1 = list(alarms(d1))
        t2 = list(alarms(d2))
        t3 = list(alarms(d3))
        t4 = list(alarms(d4))
        self.assertTrue(all(t1), '{0}\n{1}'.format(t1, et.tostring(dive)))
        self.assertTrue(all(t2), '{0}\n{1}'.format(t2, et.tostring(dive)))
        self.assertTrue(all(t3), '{0}\n{1}'.format(t3, et.tostring(dive)))
        self.assertTrue(all(t4), '{0}\n{1}'.format(t4, et.tostring(dive)))


    def test_deco(self):
        """
        Test OSTC deco data to UDDF conversion
        """
        dive = self.dives[0]
        sd = et.tostring(dive)

        wps = list(ku.xp(dive, 'uddf:samples/uddf:waypoint'))[24:181:6]

        # depth, time
        deco = ((3, 60), (12, 60), (9, 60), (12, 60), (12, 60), (3, 60), (6, 60),
                (6, 60), (6, 60), (6, 60), (12, 60), (12, 60), (9, 60), (9, 60),
                (12, 60), (12, 60), (15, 60), (12, 120), (15, 60), (9, 120), (9, 60),
                (6, 120), (6, 60), (3, 300), (3, 180), (3, 120), (3, 60),)

        self.assertEquals(deco,
            tuple((float(ku.xp_first(n, 'uddf:decostop/@decodepth')),
                   float(ku.xp_first(n, 'uddf:decostop/@duration'))) for n in wps),
            sd)

        m = [ku.xp_first(n, 'uddf:decostop/@kind') == 'mandatory' for n in wps]
        self.assertTrue(all(m), m)



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
        ver = dc.version(od.RAW_DATA_OSTC)
        self.assertEquals('OSTC 1.26', ver)


    def test_version_ostc_mk2(self):
        """
        Test OSTC Mk.2 model and version parsing from raw data
        """
        dc = OSTCMemoryDump()
        ver = dc.version(od.RAW_DATA_OSTC_MK2_190)
        self.assertEquals('OSTC Mk.2 1.90', ver)


    def test_version_ostc_n2(self):
        """
        Test OSTC N2 model and version parsing from raw data
        """
        dc = OSTCMemoryDump()
        ver = dc.version(od.RAW_DATA_OSTC_N2_191_HW)
        self.assertEquals('OSTC N2 1.91', ver)


    def test_version_191(self):
        """
        Test OSTC 1.91 and higher version parsing
        """
        dc = OSTCMemoryDump()

        ver = dc.version(od.RAW_DATA_OSTC_MK2_194)
        self.assertEquals('OSTC Mk.2 1.94', ver)

        ver = dc.version(od.RAW_DATA_OSTC_MK2_196)
        self.assertEquals('OSTC Mk.2 1.96', ver)


# vim: sw=4:et:ai
