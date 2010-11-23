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
                dump.dcdump.text)


    def test_getting_data(self):
        """Test data getting
        """
        dd = UDDFDeviceDump()
        dd.create()

        s = UDDFDeviceDump.encode('01234567890abcdef')
        dump = dd.tree.find(q('//divecomputerdump'))
        dump.dcdump = s

        self.assertEquals('01234567890abcdef', dd.get_data())


from lxml import etree as et
from cStringIO import StringIO
from datetime import datetime

import kenozooid.uddf as ku


UDDF_SAMPLE = """\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf" version="3.0.0">
  <generator>
    <name>kenozooid</name>
    <version>0.1.0</version>
    <manufacturer>
      <name>Kenozooid Team</name>
      <contact>
        <homepage>http://wrobell.it-zone.org/kenozooid/</homepage>
      </contact>
    </manufacturer>
    <datetime>2010-11-16 23:55:13</datetime>
  </generator>
  <diver>
    <owner>
      <personal>
        <firstname>Anonymous</firstname>
        <lastname>Guest</lastname>
      </personal>
      <equipment>
        <divecomputer id="su">
          <model>Sensus Ultra</model>
        </divecomputer>
      </equipment>
    </owner>
  </diver>
  <profiledata>
    <repetitiongroup>
      <dive>
        <datetime>2009-09-19 13:10:23</datetime>
        <samples>
          <waypoint>
            <depth>1.48</depth>
            <divetime>0</divetime>
            <temperature>289.02</temperature>
          </waypoint>
          <waypoint>
            <depth>2.43</depth>
            <divetime>10</divetime>
            <temperature>288.97</temperature>
          </waypoint>
          <waypoint>
            <depth>3.58</depth>
            <divetime>20</divetime>
          </waypoint>
        </samples>
      </dive>
      <dive>
        <datetime>2010-10-30 13:24:43</datetime>
        <samples>
          <waypoint>
            <depth>2.61</depth>
            <divetime>0</divetime>
            <temperature>296.73</temperature>
          </waypoint>
          <waypoint>
            <depth>4.18</depth>
            <divetime>10</divetime>
          </waypoint>
          <waypoint>
            <depth>6.25</depth>
            <divetime>20</divetime>
          </waypoint>
          <waypoint>
            <depth>8.32</depth>
            <divetime>30</divetime>
            <temperature>297.26</temperature>
          </waypoint>
        </samples>
      </dive>
    </repetitiongroup>
  </profiledata>
</uddf>
"""


class FindDataTestCase(unittest.TestCase):
    """
    Data search within UDDF tests.
    """
    def test_parsing(self):
        """Test basic XML parsing routine"""
        f = StringIO(UDDF_SAMPLE)
        depths = list(ku.parse(f, '//uddf:waypoint//uddf:depth/text()'))
        self.assertEqual(7, len(depths))

        expected = ['1.48', '2.43', '3.58', '2.61', '4.18', '6.25', '8.32']
        self.assertEqual(expected, depths)


    def test_dive_data(self):
        """Test parsing UDDF default dive data"""
        f = StringIO(UDDF_SAMPLE)
        node = ku.parse(f, '//uddf:dive[1]').next()
        dive = ku.dive_data(node)
        self.assertEquals(datetime(2009, 9, 19, 13, 10, 23), dive.time)


    def test_profile_data(self):
        """Test parsing UDDF default dive profile data"""
        f = StringIO(UDDF_SAMPLE)
        node = ku.parse(f, '//uddf:dive[2]').next()
        profile = list(ku.dive_profile(node))
        self.assertEquals(4, len(profile))

        self.assertEquals((0, 2.61, 296.73), profile[0])
        self.assertEquals((10, 4.18, None), profile[1])
        self.assertEquals((20, 6.25, None), profile[2])
        self.assertEquals((30, 8.32, 297.26), profile[3])



class CreateDataTestCase(unittest.TestCase):
    """
    UDDF creation and saving tests
    """
    def test_create_basic(self):
        """
        Test basic UDDF file creation.
        """
        now = datetime.now()
        doc = ku.create(time=now)
        q = '//uddf:generator/uddf:datetime/text()'
        dt = doc.xpath(q, namespaces=ku._NSMAP)

        self.assertEquals(now.strftime(ku.FMT_DATETIME), dt[0])


    def test_save(self):
        """
        Test UDDF data saving
        """
        doc = ku.create()
        f = StringIO()
        ku.save(doc, f)
        s = f.getvalue()
        self.assertFalse('uddf:' in s)
        f.close() # check if file closing is possible

        preamble = """\
<?xml version='1.0' encoding='utf-8'?>
<uddf xmlns="http://www.streit.cc/uddf" version="3.0.0">\
"""
        self.assertTrue(s.startswith(preamble), s)



class PostprocessingTestCase(unittest.TestCase):
    """
    UDDF postprocessing tests.
    """
    def test_reorder(self):
        """Test UDDF reordering
        """
        doc = et.parse(StringIO("""
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
        ku.reorder(doc)

        f = StringIO()
        ku.save(doc, f)

        f = StringIO(f.getvalue())

        nodes = list(ku.parse(f, '//uddf:repetitiongroup'))
        self.assertEquals(1, len(nodes))
        nodes = list(ku.parse(f, '//uddf:dive'))
        self.assertEquals(2, len(nodes))

        # check the order of dives
        times = list(ku.parse(f, '//uddf:dive/uddf:datetime/text()'))
        self.assertEquals(['2009-03-02 23:02', '2009-04-02 23:02'], times)


# vim: sw=4:et:ai
