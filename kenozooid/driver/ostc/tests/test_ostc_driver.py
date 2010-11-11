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

OSTC_UDDF_DUMP = """\
<?xml version='1.0' encoding='utf-8'?>
<uddf xmlns="http://www.streit.cc/uddf" version="3.0.0">
  <generator>
    <name>kenozooid</name>
    <version>0.1.0</version>
    <datetime>2009-02-15 18:26</datetime>
    <manufacturer>
      <name>Kenozooid Team</name>
      <contact>
        <homepage>http://wrobell.it-zone.org/kenozooid/</homepage>
      </contact>
    </manufacturer>
  </generator>
  <diver>
    <owner>
      <personal>
        <firstname>Anonymous</firstname>
        <lastname>Guest</lastname>
      </personal>
      <equipment>
        <divecomputer id='ostc'>
          <model>OSTC Mk.1</model>
        </divecomputer>
      </equipment>
    </owner>
  </diver>
  <divecomputercontrol>
    <divecomputerdump>
      <link ref='ostc'/>
      <datetime>2009-02-15 18:26</datetime>
      <dcdump>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</dcdump>
    </divecomputerdump>
  </divecomputercontrol>
</uddf>
"""


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
        dd.parse(StringIO(OSTC_UDDF_DUMP))

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


