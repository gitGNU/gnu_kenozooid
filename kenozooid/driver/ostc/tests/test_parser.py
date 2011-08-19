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

from . import data as od


class ParserTestCase(unittest.TestCase):
    """
    OSTC binary data parsing tests.
    """
    def test_data_parsing(self):
        """Test OSTC data parsing (< 1.91)
        """
        dump = ostc_parser.status(od.RAW_DATA_OSTC)

        self.assertEquals(b'\xaa' * 5 + b'\x55', dump.preamble)

        # first dive is deleted one so no \xfa\xfa
        self.assertEquals(b'\xfa\x20', dump.profiles[:2])

        self.assertEquals(4142, dump.voltage)

        # ver. 1.26
        self.assertEquals(1, dump.ver1)
        self.assertEquals(26, dump.ver2)

        self.assertEquals(32768, dump.profiles)


    def test_data_parsing(self):
        """Test OSTC data parsing (>= 1.91)
        """
        dump = ostc_parser.status(od.RAW_DATA_OSTC_MK2_194)

        self.assertEquals(b'\xaa' * 5 + b'\x55', dump.preamble)

        self.assertEquals(4221, dump.voltage)

        # ver. 1.94
        self.assertEquals(1, dump.ver1)
        self.assertEquals(94, dump.ver2)
        
        self.assertEquals(65536, len(dump.profiles))


    def test_eeprom_parsing(self):
        """Test EEPROM data parsing
        """
        dump = ostc_parser.status(od.RAW_DATA_OSTC)
        eeprom = dump.eeprom

        self.assertEquals(155, eeprom.serial)
        self.assertEquals(23, eeprom.dives)
        self.assertEquals(252, len(eeprom.data))


    def test_profile_split(self):
        """
        Test OSTC data profile splitting (< 1.91)
        """
        dump = ostc_parser.status(od.RAW_DATA_OSTC)
        profile = tuple(ostc_parser.profiles(dump.profiles))
        # five dives expected
        self.assertEquals(5, len(profile))
        for header, block in profile:
            self.assertEquals(b'\xfa\xfa', header[:2])
            self.assertEquals(0x20, header[2])
            self.assertEquals(b'\xfb\xfb', header[-2:])
            self.assertEquals(47, len(header))
            self.assertEquals(b'\xfd\xfd', block[-2:])


    def test_profile_split_191(self):
        """
        Test OSTC data profile splitting (>= 1.91)
        """
        dump = ostc_parser.status(od.RAW_DATA_OSTC_MK2_194)
        profile = tuple(ostc_parser.profiles(dump.profiles))
        # five dives expected
        self.assertEquals(9, len(profile))
        for i, (header, block) in enumerate(profile):
            self.assertEquals(b'\xfa\xfa', header[:2])
            if i < 2:
                self.assertEquals(0x20, header[2])
                self.assertEquals(47, len(header))
            else:
                self.assertEquals(0x21, header[2])
                self.assertEquals(57, len(header))
            self.assertEquals(b'\xfb\xfb', header[-2:])
            self.assertEquals(b'\xfd\xfd', block[-2:])


    def test_dive_profile_header_parsing(self):
        """Test dive profile header parsing
        """
        dump = ostc_parser.status(od.RAW_DATA_OSTC)
        profile = tuple(ostc_parser.profiles(dump.profiles))
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
        dump = ostc_parser.status(od.RAW_DATA_OSTC)
        profiles = tuple(ostc_parser.profiles(dump.profiles))
        h, p = profiles[0]
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
        data = tuple(ostc_parser.profiles(ku._dump_decode(od.DATA_OSTC_BROKEN)))
        assert 32 == len(data)

        # dive no 31 is broken (count from 0)
        h, p = data[30]
        header = ostc_parser.header(h)
        dive_data = ostc_parser.dive_data(header, p)
        self.assertRaises(ValueError, tuple, dive_data)



# vim: sw=4:et:ai
