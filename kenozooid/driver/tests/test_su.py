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
Reefnet Sensus Ultra driver tests.
"""

from collections import namedtuple
from datetime import datetime
from binascii import unhexlify
import lxml.etree as et
import unittest

import kenozooid.uddf as ku
from kenozooid.driver.su import SensusUltraDataParser, _handshake, _dive_header

SU_DATA_DOWNLOAD_TIME = datetime(2010, 2, 22, 21, 34, 22)
SU_DATA_INTERVAL = 10
SU_DATA = \
   r'QlpoOTFBWSZTWXY6bxUAAUJ/////////////////////////////////////////////4G' \
    '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'


def _dump():
    Dump = namedtuple('Dump', 'datetime data')
    data = ku._dump_decode(SU_DATA)
    return Dump(datetime=SU_DATA_DOWNLOAD_TIME, data=data)


class SensusUltraUDDFTestCase(unittest.TestCase):
    """
    Sensus Ultra data to UDDF format conversion tests.
    """
    def test_profile_conversion(self):
        """
        Test Sensus Ultra profile data conversion
        """
        dump = _dump()

        dumper = SensusUltraDataParser()
        dives = list(dumper.dives(dump))

        # 43 dives
        self.assertEquals(43, len(dives))

        dive = dives[-1] # su stores data from last to first
        self.assertEquals(datetime(2009, 9, 19, 13, 14, 40), dive.datetime)

        self.assertEquals(12.0, dive.depth)
        self.assertEquals(170, dive.duration)
        self.assertEquals(288.6, dive.temp)
        self.assertTrue(dive.avg_depth is None)

        # 18 samples for first dive
        samples = list(dive.profile)
        self.assertEquals(18, len(samples))

        # su driver calculates the max depth and min temperature
        self.assertEquals(12.0, round(max(s.depth for s in samples), 1))
        self.assertEquals(288.6, min(s.temp for s in samples
            if s.temp is not None))

        # check first sample, UDDF obligatory one
        self.assertEquals(0, samples[0].time)
        self.assertEquals(0.0, samples[0].depth)

        # check if second sample does not start with 0 time
        self.assertEquals(SU_DATA_INTERVAL, samples[1].time)

        # check last UDDF required sample
        self.assertEquals(170, samples[-1].time) # dive.duration above should
                                                 # equal to this value, too
        self.assertEquals(0.0, samples[-1].depth)

        # check time of the one sample before last
        self.assertEquals(160, samples[-2].time)

        # check the one before last and last samples times
        t1 = samples[-2].time
        t2 = samples[-1].time
        self.assertEquals(SU_DATA_INTERVAL, t2 - t1) 



class ParserTestCase(unittest.TestCase):
    """
    Sensus Ultra data parsing test case.
    """

    def test_handshake(self):
        """
        Test Sensus Ultra handshake data parsing
        """
        data = unhexlify(b'0203641d4ebee30302007a837f018b000a0057040f000100')
        v = _handshake(data)
        self.assertEquals(3, v.ver2)
        self.assertEquals(2, v.ver1)
        self.assertEquals(7524, v.serial)
        self.assertEquals(65257038, v.time)


    def test_dive_header(self):
        """
        Test Sensus Ultra dive header data parsing
        """
        data = unhexlify(b'00000000dc2866020a0057040f000100')
        v = _dive_header(data)
        self.assertEquals(40249564, v.time)
        self.assertEquals(10, v.interval)
        self.assertEquals(1111, v.threshold)
        self.assertEquals(15, v.endcount)
        self.assertEquals(1, v.averaging)


class DataParserTestCase(unittest.TestCase):
    """
    Sensus Ultra data parser driver tests.
    """
    def test_version(self):
        """
        Test Sensus Ultra version parsing from raw data
        """
        data = ku._dump_decode(SU_DATA)
        drv = SensusUltraDataParser()
        ver = drv.version(data)
        self.assertEquals('Sensus Ultra 3.2', ver)


    def test_gases(self):
        """
        Test Sensus Ultra gases parsing from raw data
        """
        # no gas info stored by Sensus Ultra
        data = ku._dump_decode(SU_DATA)
        drv = SensusUltraDataParser()
        
        self.assertEquals((), tuple(drv.gases(data)))



# vim: sw=4:et:ai
