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
UDDF file format tests.
"""

import unittest
from lxml import etree
import lxml.objectify as eto
from datetime import datetime
from StringIO import StringIO

import kenozooid
from kenozooid.uddf import UDDFFile, UDDFProfileData, UDDFDeviceDump, \
        q, has_deco, has_temp

class UDDFTestCase(unittest.TestCase):
    """
    UDDF file format tests.
    """
    def test_creation(self):
        """Test UDDF creation
        """
        uf = UDDFFile()
        uf.create()
        self.assertFalse(uf.tree is None)

        root = uf.tree.getroot()
        self.assertEquals('3.0.0', root.get('version')) # check UDDF version
        self.assertEquals('kenozooid', root.generator.name.text)
        self.assertEquals(kenozooid.__version__, root.generator.version.text)


    def test_time_parsing(self):
        """Test UDDF time parsing
        """
        uf = UDDFProfileData()
        uf.parse(StringIO("""
<uddf xmlns="http://www.streit.cc/uddf">
<profiledata>
<repetitiongroup>
<dive>
    <datetime>2009-03-02 23:02</datetime>
</dive>
</repetitiongroup>
</profiledata>
</uddf>
"""))
        dt = uf.get_datetime(uf.tree.find(q('//dive')))
        self.assertEquals(datetime(2009, 3, 2, 23, 2), dt)


    def test_q(self):
        """Test conversion to qualified tag names and ElementPath expressions"""
        self.assertEquals('{http://www.streit.cc/uddf}name', q('name'))
        self.assertEquals('//{http://www.streit.cc/uddf}name', q('//name'))
        self.assertEquals('{http://www.streit.cc/uddf}samples/' \
                '{http://www.streit.cc/uddf}waypoint', q('samples/waypoint'))


    def test_has_deco(self):
        """Test checking deco waypoint.
        """
        w = eto.XML('<waypoint><alarm>deco</alarm></waypoint>')
        self.assertTrue(has_deco(w))

        w = eto.XML('<waypoint><alarm>error</alarm></waypoint>')
        self.assertFalse(has_deco(w))

        w = eto.XML('<waypoint></waypoint>')
        self.assertFalse(has_deco(w))

        # there can be different alarms
        w = eto.XML('<waypoint><alarm>error</alarm><alarm>deco</alarm></waypoint>')
        self.assertTrue(has_deco(w))


    def test_has_temp(self):
        """Test checking waypoint with temperature.
        """
        w = eto.XML('<waypoint><temperature>12</temperature></waypoint>')
        self.assertTrue(has_temp(w))

        w = eto.XML('<waypoint></waypoint>')
        self.assertFalse(has_temp(w))



class UDDFCompactTestCase(unittest.TestCase):
    def test_uddf_compact(self):
        """Test UDDF compact
        """
        pd = UDDFProfileData()
        pd.parse(StringIO("""
<uddf xmlns="http://www.streit.cc/uddf">
<profiledata>
<repetitiongroup>
<dive>
    <datetime>2009-03-02 23:02</datetime>
</dive>
<dive>
    <datetime>2009-04-02 23:02</datetime>
</dive>
<dive>
    <datetime>2009-04-02 23:02</datetime>
</dive>
<dive>
    <datetime>2009-03-02 23:02</datetime>
</dive>
</repetitiongroup>
<repetitiongroup> <!-- one more repetition group which shall be removed -->
<dive>
    <datetime>2009-03-02 23:02</datetime>
</dive>
</repetitiongroup>
</profiledata>
</uddf>
"""))
        pd.compact()

        tree = pd.tree

        self.assertEquals(1, len(tree.findall(q('//repetitiongroup'))))
        dives = tree.findall(q('//dive'))
        self.assertEquals(2, len(dives))

        # check the order of dives (ordered by dive time)
        dt = pd.get_datetime(dives[0])
        self.assertEquals(datetime(2009, 3, 2, 23, 2), dt)

        dt = pd.get_datetime(dives[1])
        self.assertEquals(datetime(2009, 4, 2, 23, 2), dt)



class UDDFDeviceDumpTestCase(unittest.TestCase):
    """
    Tests for UDDF file containing device dump data.
    """
    def test_creation(self):
        """Test UDDF device dump file creation
        """
        uf = UDDFDeviceDump()
        uf.create()
        self.assertFalse(uf.tree is None)

        root = uf.tree.getroot()
        self.assertEquals('3.0.0', root.get('version')) # check UDDF version
        self.assertEquals('kenozooid', root.generator.name.text)
        self.assertEquals(kenozooid.__version__, root.generator.version.text)
        self.assertTrue(q('divecomputercontrol') in [el.tag for el in root.iterchildren()])
        dc = root.divecomputercontrol
        self.assertTrue(q('divecomputerdump') in [el.tag for el in dc.iterchildren()])


    def test_encoding(self):
        """Test data encoding
        """
        s = UDDFDeviceDump.encode('01234567890abcdef')
        self.assertEquals('QlpoOTFBWSZTWZdWXlwAAAAJAH/gPwAgACKMmAAUwAE0xwH5Gis6xNXmi7kinChIS6svLgA=', s)


    def test_decoding(self):
        """Test data decoding
        """
        s = UDDFDeviceDump.decode('QlpoOTFBWSZTWZdWXlwAAAAJAH/gPwAgACKMmAAUwAE0xwH5Gis6xNXmi7kinChIS6svLgA=')
        self.assertEquals('01234567890abcdef', s)


    def test_setting_data(self):
        """Test data setting
        """
        dd = UDDFDeviceDump()
        dd.create()
        dd.set_model('tt', 'Test Model')

        dd.set_data('01234567890abcdef')
        
        dump = dd.tree.find(q('//divecomputerdump'))
        self.assertEquals('QlpoOTFBWSZTWZdWXlwAAAAJAH/gPwAgACKMmAAUwAE0xwH5Gis6xNXmi7kinChIS6svLgA=',
                dump.dcdata.text)


    def test_getting_data(self):
        """Test data getting
        """
        dd = UDDFDeviceDump()
        dd.create()

        s = UDDFDeviceDump.encode('01234567890abcdef')
        dump = dd.tree.find(q('//divecomputerdump'))
        dump.dcdata = s

        self.assertEquals('01234567890abcdef', dd.get_data())


