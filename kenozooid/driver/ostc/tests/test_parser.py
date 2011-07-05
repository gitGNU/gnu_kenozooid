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
OSTC driver binary parser routines tests.
"""

import bz2
import base64
import unittest

import kenozooid.driver.ostc.parser as ostc_parser
import kenozooid.uddf as ku

OSTC_DATA = \
   r'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'


# 32 dives in total, including broken dive no 30 started at 2010-06-05 11:49
# (dives are not in order)
OSTC_DATA_BROKEN = \
   r'QlpoOTFBWSZTWQmRDagAOnT/////////////////////////////////////////////4D' \
    '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' \
    'IbUA==' \


class ParserTestCase(unittest.TestCase):
    """
    OSTC binary data parsing tests.

    :Attributes:
     dump_data
        OSTC dump data from OSTC_DATA.

    """
    def setUp(self):
        """
        Create test dump data.
        """
        self.dump_data = ku._dump_decode(OSTC_DATA)


    def test_status_parsing(self):
        """Test status parsing
        """
        dump = ostc_parser.status(self.dump_data)

        self.assertEquals(b'\xaa' * 5 + b'\x55', dump.preamble)

        # first dive is deleted one so no \xfa\xfa
        self.assertEquals(b'\xfa\x20', dump.profile[:2])

        self.assertEquals(4142, dump.voltage)

        # ver. 1.26
        self.assertEquals(1, dump.ver1)
        self.assertEquals(26, dump.ver2)


    def test_eeprom_parsing(self):
        """Test EEPROM data parsing
        """
        dump = ostc_parser.status(self.dump_data)
        eeprom = dump.eeprom

        self.assertEquals(155, eeprom.serial)
        self.assertEquals(23, eeprom.dives)
        self.assertEquals(252, len(eeprom.data))


    def test_profile_split(self):
        """Test profile splitting
        """
        dump = ostc_parser.status(self.dump_data)
        profile = tuple(ostc_parser.profile(dump.profile))
        # five dives expected
        self.assertEquals(5, len(profile))
        for header, block in profile:
            self.assertEquals(b'\xfa\xfa', header[:2])
            self.assertEquals(b'\xfb\xfb', header[-2:])
            self.assertEquals(b'\xfd\xfd', block[-2:])


    def test_dive_profile_header_parsing(self):
        """Test dive profile header parsing
        """
        dump = ostc_parser.status(self.dump_data)
        profile = tuple(ostc_parser.profile(dump.profile))
        header = ostc_parser.header(profile[0][0])
        self.assertEquals(0xfafa, header.start)
        self.assertEquals(0xfbfb, header.end)
        self.assertEquals(0x20, header.version)
        self.assertEquals(1, header.month)
        self.assertEquals(31, header.day)
        self.assertEquals(9, header.year)
        self.assertEquals(23, header.hour)
        self.assertEquals(41, header.minute)
        self.assertEquals(7500, header.max_depth)
        self.assertEquals(32, header.dive_time_m)
        self.assertEquals(9, header.dive_time_s)
        self.assertEquals(275, header.min_temp)
        self.assertEquals(1025, header.surface_pressure)
        self.assertEquals(920, header.desaturation)
        self.assertEquals(21, header.gas1)
        self.assertEquals(32, header.gas2)
        self.assertEquals(21, header.gas3)
        self.assertEquals(21, header.gas4)
        self.assertEquals(21, header.gas5)
        self.assertEquals(32, header.gas6)
        self.assertEquals(1, header.gas)
        self.assertEquals(1, header.ver1)
        self.assertEquals(26, header.ver2)
        self.assertEquals(4066, header.voltage)
        self.assertEquals(10, header.sampling)
        self.assertEquals(38, header.div_temp)
        self.assertEquals(38, header.div_deco)
        self.assertEquals(32, header.div_tank)
        self.assertEquals(48, header.div_ppo2)
        self.assertEquals(0, header.div_deco_debug)
        self.assertEquals(0, header.div_res2)
        self.assertEquals(0, header.spare)


    def test_dive_profile_block_parsing(self):
        """Test dive profile data block parsing
        """
        dump = ostc_parser.status(self.dump_data)
        profile = tuple(ostc_parser.profile(dump.profile))
        h, p = profile[0]
        header = ostc_parser.header(h)
        dive = tuple(ostc_parser.dive_data(header, p))
        # 217 samples, but dive time is 32:09 (sampling 10)
        self.assertEquals(193, len(dive))

        self.assertAlmostEquals(3.0, dive[0].depth, 3)
        self.assertFalse(dive[0].alarm)
        self.assertAlmostEquals(23.0, dive[1].depth, 3)
        self.assertFalse(dive[1].alarm)

        self.assertAlmostEquals(29.5, dive[5].temp, 3)
        self.assertEquals(5, dive[5].alarm)
        self.assertEquals(2, dive[5].current_gas)
        self.assertEquals(0, dive[5].deco_depth)
        self.assertEquals(7, dive[5].deco_time)

        self.assertAlmostEquals(29.0, dive[23].temp, 3)
        self.assertFalse(dive[23].alarm)
        self.assertFalse(dive[23].current_gas)
        self.assertEquals(3, dive[23].deco_depth)
        self.assertEquals(1, dive[23].deco_time)


    def test_sample_data_parsing(self):
        """Test sample data parsing
        """
        from struct import unpack

        # temp = 50 (5 degrees)
        # deco = NDL/160
        data = b'\x2c\x01\x84\x32\x00\x00\xa0'
        v = ostc_parser.sample_data(data, 3, 8, 4, 2)
        self.assertEquals(50, unpack('<H', v)[0])

        # 5th sample and divisor sampling == 4 => no data
        v = ostc_parser.sample_data(data, 3, 5, 4, 2)
        self.assertFalse(v)

        d, t = ostc_parser.sample_data(data, 5, 8, 4, 2)
        self.assertEquals(0, d)
        self.assertEquals(0xa0, t)


    def test_divisor(self):
        """Test getting divisor information
        """
        divisor, size = ostc_parser.divisor(38)
        self.assertEquals(6, divisor)
        self.assertEquals(2, size)

        divisor, size = ostc_parser.divisor(32)
        self.assertEquals(0, divisor)
        self.assertEquals(2, size)

        divisor, size = ostc_parser.divisor(48)
        self.assertEquals(0, divisor)
        self.assertEquals(3, size)


    def test_flag_byte_split(self):
        """Test splitting profile flag byte
        """
        size, event = ostc_parser.flag_byte(132)
        self.assertEquals(4, size)
        self.assertEquals(1, event)

        size, event = ostc_parser.flag_byte(5)
        self.assertEquals(5, size)
        self.assertEquals(0, event)


    def test_invalid_profile(self):
        """Test parsing invalid profile
        """
        data = tuple(ostc_parser.profile(ku._dump_decode(OSTC_DATA_BROKEN)))
        assert 32 == len(data)

        # dive no 31 is broken (count from 0)
        h, p = data[30]
        header = ostc_parser.header(h)
        dive_data = ostc_parser.dive_data(header, p)
        self.assertRaises(ValueError, tuple, dive_data)



# vim: sw=4:et:ai
