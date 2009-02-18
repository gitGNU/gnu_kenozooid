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
OSTC driver binary parser routines tests.
"""

import unittest

from kenozooid.driver.ostc import byte, pressure
from kenozooid.driver.ostc import OSTCMemoryDump
import kenozooid.driver.ostc.parser as ostc_parser
from kenozooid.uddf import create

class ParserTestCase(unittest.TestCase):
    """
    OSTC binary data parsing tests.
    """
    def test_status_parsing(self):
        """Test status parsing
        """
        f = open('dumps/ostc-01.dump')
        dump = ostc_parser.status(''.join(f))

        self.assertEquals('\xaa' * 5 + '\x55', dump.preamble)

        # first dive is deleted one so no \xfa\xfa
        self.assertEquals('\xfa\x20', dump.profile[:2])

        self.assertEquals(4142, dump.voltage)

        # ver. 1.26
        self.assertEquals(1, dump.ver1)
        self.assertEquals(26, dump.ver2)


    def test_profile_split(self):
        """Test profile splitting
        """
        f = open('dumps/ostc-01.dump')
        dump = ostc_parser.status(''.join(f))
        profile = tuple(ostc_parser.profile(dump.profile))
        # five dives expected
        self.assertEquals(5, len(profile))
        for header, block in profile:
            self.assertEquals('\xfa\xfa', header[:2])
            self.assertEquals('\xfb\xfb', header[-2:])
            self.assertEquals('\xfd\xfd', block[-2:])


    def test_dive_profile_header_parsing(self):
        """Test dive profile header parsing
        """
        f = open('dumps/ostc-01.dump')
        dump = ostc_parser.status(''.join(f))
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
        self.assertEquals(0, header.div_res1)
        self.assertEquals(0, header.div_res2)
        self.assertEquals(0, header.spare)


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
