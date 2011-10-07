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
Tests for Kenozooid data functions.
"""

from datetime import datetime
import unittest

import kenozooid.data as kd

class DivesTestCase(unittest.TestCase):
    """
    Tests for dive sorting, duplicates removal, etc.
    """
    def test_uniq(self):
        """
        Test removal of duplicate removal
        """
        dives = (kd.Dive(datetime=datetime(2011, 5, 5)),
                kd.Dive(datetime=datetime(2011, 5, 5)),
                kd.Dive(datetime=datetime(2011, 5, 6)))
        ud = list(kd.uniq_dives(dives))
        self.assertEquals(2, len(ud))


    def test_gas_basic(self):
        """
        Test basic gas data creation
        """
        e = kd.Gas(id='air', name='Air', o2=21, he=0)
        self.assertEquals(e, kd.gas(21, 0))

        e = kd.Gas(id='o2', name='O2', o2=100, he=0)
        self.assertEquals(e, kd.gas(100, 0))


    def test_gas_ean(self):
        """
        Test nitrox gas data creation
        """
        e = kd.Gas(id='ean32', name='EAN32', o2=32, he=0)
        self.assertEquals(e, kd.gas(32, 0))

        e = kd.Gas(id='ean40', name='EAN40', o2=40, he=0)
        self.assertEquals(e, kd.gas(40, 0))

        e = kd.Gas(id='ean50', name='EAN50', o2=50, he=0)
        self.assertEquals(e, kd.gas(50, 0))

        e = kd.Gas(id='ean80', name='EAN80', o2=80, he=0)
        self.assertEquals(e, kd.gas(80, 0))


    def test_gas_trimix(self):
        """
        Test trimix gas data creation
        """
        21/35, 18/45 and 15/55
        e = kd.Gas(id='tx2135', name='TX 21/35', o2=21, he=35)
        self.assertEquals(e, kd.gas(21, 35))

        e = kd.Gas(id='tx1845', name='TX 18/45', o2=18, he=45)
        self.assertEquals(e, kd.gas(18, 45))

        e = kd.Gas(id='tx1555', name='TX 15/55', o2=15, he=55)
        self.assertEquals(e, kd.gas(15, 55))


# vim: sw=4:et:ai
