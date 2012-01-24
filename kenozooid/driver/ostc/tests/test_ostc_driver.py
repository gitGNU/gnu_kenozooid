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

"""
OSTC driver tests.
"""

from collections import namedtuple
from datetime import datetime
import unittest

import kenozooid.data as kd
import kenozooid.driver.ostc.parser as ostc_parser
from kenozooid.driver.ostc import pressure, OSTCDataParser

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



class DataModelTestCase(unittest.TestCase):
    """
    OSTC data to data model format conversion tests.

    :Attributes:
     dives
        List of dives parsed from DATA_OSTC.
    """
    def setUp(self):
        super(DataModelTestCase, self).setUp()

        dump = kd.BinaryData(datetime=datetime.now(), data=od.RAW_DATA_OSTC)
        dc = OSTCDataParser()
        self.dives = list(dc.dives(dump))


    def test_conversion(self):
        """
        Test basic OSTC data to data model conversion
        """
        # five dives
        self.assertEquals(5, len(self.dives))

        # 193 samples for first dive
        dive = self.dives[0]
        samples = list(dive.profile)
        self.assertEquals(195, len(samples))

        self.assertEquals(datetime(2009, 1, 31, 23, 8, 41), dive.datetime)
        self.assertEquals(75.0, dive.depth)
        self.assertEquals(1939, dive.duration)
        self.assertEquals(300.65, dive.temp) # 27.45C


    def test_gas(self):
        """
        Test OSTC gas data to data model conversion
        """
        dump = kd.BinaryData(datetime=datetime.now(),
                data=od.RAW_DATA_OSTC_MK2_196)
        dc = OSTCDataParser()
        dive = list(dc.dives(dump))[7]
        samples = list(dive.profile)
        self.assertEquals('tx1633', samples[0].gas.id)
        self.assertEquals('tx1633', samples[1360].gas.id)
        self.assertEquals('o2', samples[1372].gas.id)
        self.assertEquals('ean47', samples[1491].gas.id)


    def test_gas_info(self):
        """
        Test OSTC gas fetching from header
        """
        dives = ostc_parser.profiles(od.RAW_DATA_OSTC_MK2_194)
        header, profile = list(dives)[7]
        header = ostc_parser.header(header)
        dc = OSTCDataParser()

        self.assertEquals('air', dc._get_gas(header, 1).id)
        self.assertEquals('ean47', dc._get_gas(header, 2).id)
        self.assertEquals('o2', dc._get_gas(header, 3).id)
        self.assertEquals('tx1340', dc._get_gas(header, 4).id)
        self.assertEquals('tx1737', dc._get_gas(header, 5).id)
        self.assertEquals('tx1050', dc._get_gas(header, 6).id)


    def test_ppo2_set(self):
        """
        Test OSTC ppO2 change
        """
        dump = kd.BinaryData(datetime=datetime.now(),
                data=od.RAW_DATA_OSTC_MK2_196)
        dc = OSTCDataParser()
        dive = list(dc.dives(dump))[7]
        samples = list(dive.profile)
        self.assertEquals(104000, samples[1].setpoint)
        self.assertEquals(137000, samples[166].setpoint)
        self.assertEquals(127000, samples[1385].setpoint)


    def test_deco_alarm(self):
        """
        Test OSTC deco alarm data to data model conversion
        """
        dive = self.dives[3] # dive no 3 contains deco alarms
        samples = list(dive.profile)

        d1 = samples[587:594]
        d2 = samples[743:749]
        d3 = samples[972:976]
        d4 = samples[1320:1343]

        # check if all deco waypoints have appropriate alarms
        def alarms(samples):
            return (s.alarm == ('deco',) for s in samples)

        t1 = list(alarms(d1))
        t2 = list(alarms(d2))
        t3 = list(alarms(d3))
        t4 = list(alarms(d4))
        self.assertTrue(all(t1), '{0}\n{1}'.format(t1, d1))
        self.assertTrue(all(t2), '{0}\n{1}'.format(t2, d2))
        self.assertTrue(all(t3), '{0}\n{1}'.format(t3, d3))
        self.assertTrue(all(t4), '{0}\n{1}'.format(t4, d4))


    def test_deco(self):
        """
        Test OSTC deco data to data model conversion
        """
        dive = self.dives[0]
        samples = list(dive.profile)[24:181:6]

        # depth, time
        deco = ((3, 60), (12, 60), (9, 60), (12, 60), (12, 60), (3, 60), (6, 60),
                (6, 60), (6, 60), (6, 60), (12, 60), (12, 60), (9, 60), (9, 60),
                (12, 60), (12, 60), (15, 60), (12, 120), (15, 60), (9, 120), (9, 60),
                (6, 120), (6, 60), (3, 300), (3, 180), (3, 120), (3, 60),)

        self.assertEquals(deco,
            tuple((float(s.deco_depth), float(s.deco_time)) for s in samples))


    def test_no_avg_depth(self):
        """
        Test OSTC1 no average depth parsing
        """
        dive = self.dives[0]
        self.assertTrue(dive.avg_depth is None)


    def test_avg_depth_191(self):
        """
        Test OSTC 1.91 average depth parsing
        """
        dc = OSTCDataParser()

        dump = kd.BinaryData(datetime=datetime.now(),
                data=od.RAW_DATA_OSTC_MK2_196)
        dive = next(dc.dives(dump))
        self.assertEquals(7.3, dive.avg_depth)

        # do not use 1st and 2nd dives as they were generated with firmware
        # ver < 1.91
        dump = kd.BinaryData(datetime=datetime.now(),
                data=od.RAW_DATA_OSTC_MK2_194)
        dive = list(dc.dives(dump))[2]
        self.assertEquals(26.05, dive.avg_depth)



class DataParserTestCase(unittest.TestCase):
    """
    OSTC data parser tests.

    :Attributes:
     dump_data
        OSTC raw data from OSTC_DATA.

    """
    def test_version_ostc(self):
        """
        Test OSTC model and version parsing from raw data
        """
        dc = OSTCDataParser()
        ver = dc.version(od.RAW_DATA_OSTC)
        self.assertEquals('OSTC 1.26', ver)


    def test_version_ostc_mk2(self):
        """
        Test OSTC Mk.2 model and version parsing from raw data
        """
        dc = OSTCDataParser()
        ver = dc.version(od.RAW_DATA_OSTC_MK2_190)
        self.assertEquals('OSTC Mk.2 1.90', ver)


    def test_version_ostc_n2(self):
        """
        Test OSTC 2N model and version parsing from raw data
        """
        dc = OSTCDataParser()
        ver = dc.version(od.RAW_DATA_OSTC_N2_191_HW)
        self.assertEquals('OSTC 2N 1.91', ver)


    def test_version_191(self):
        """
        Test OSTC 1.91 and higher version parsing
        """
        dc = OSTCDataParser()

        ver = dc.version(od.RAW_DATA_OSTC_MK2_194)
        self.assertEquals('OSTC Mk.2 1.94', ver)

        ver = dc.version(od.RAW_DATA_OSTC_MK2_196)
        self.assertEquals('OSTC Mk.2 1.96', ver)


# vim: sw=4:et:ai
