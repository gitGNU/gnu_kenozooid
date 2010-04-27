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
OSTC driver tests.
"""

import unittest
import lxml.objectify as eto
from cStringIO import StringIO

from kenozooid.driver.ostc import pressure
from kenozooid.driver.ostc import OSTCMemoryDump
import kenozooid.driver.ostc.parser as ostc_parser
from kenozooid.uddf import UDDFProfileData, UDDFDeviceDump, q


class ConversionTestCase(unittest.TestCase):
    def test_pressure_conversion(self):
        """Test depth to pressure conversion
        """
        self.assertEquals(11, pressure(1))
        self.assertEquals(30, pressure(20))
        self.assertEquals(25, pressure(15.5))



class UDDFTestCase(unittest.TestCase):
    """
    OSTC data to UDDF format conversion tests.
    """
    def setUp(self):
        super(UDDFTestCase, self).setUp()

        pd = UDDFProfileData()
        pd.create()

        dd = UDDFDeviceDump()
        dd.open('dumps/ostc-dump-01.uddf')

        dumper = OSTCMemoryDump()
        dumper.convert(dd.tree, StringIO(dd.get_data()), pd.tree)
        self.pd = pd
        self.tree = pd.tree


    def test_conversion(self):
        """Test basic OSTC data to UDDF conversion
        """
        # five dives
        self.assertEquals(5, len(self.tree.findall(q('//dive'))))

        # 193 samples for first dive
        dive = self.tree.find(q('//dive'))
        data = dive.findall(q('samples/waypoint'))
        self.assertEquals(193, len(data))

        self.assertEquals('2009-01-31 23:08:51', dive.datetime)

        self.pd.clean()
        self.pd.validate()


    def test_deco(self):
        """Test OSTC deco data to UDDF conversion
        """
        # get first dive, there are two deco periods
        dive = self.tree.find(q('//dive'))
        wps = dive.findall(q('samples/waypoint'))
        d1 = wps[155:161]
        d2 = wps[167:185]

        # check if all deco waypoints has appropriate alarms
        t1 = list(hasattr(d, 'alarm') and d.alarm.text == 'deco' for d in d1)
        t2 = list(hasattr(d, 'alarm') and d.alarm.text == 'deco' for d in d2)
        self.assertTrue(all(t1), t1)
        self.assertTrue(all(t2), t2)


