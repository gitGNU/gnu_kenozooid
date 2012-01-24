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
UDDF file format tests.
"""

from lxml import etree as et
from io import BytesIO
from datetime import datetime
from functools import partial
from dirty.xml import xml
import unittest

import kenozooid.uddf as ku
import kenozooid.data as kd


UDDF_PROFILE = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
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
      <dive id='d01'>
        <informationbeforedive>
            <datetime>2009-09-19T13:10:23</datetime>
        </informationbeforedive>
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
        <informationafterdive>
            <diveduration>20</diveduration>
            <greatestdepth>30.2</greatestdepth>
            <lowesttemperature>251.4</lowesttemperature>
            <averagedepth>10.1</averagedepth>
        </informationafterdive>
      </dive>
      <dive id='d02'>
        <informationbeforedive>
            <datetime>2010-10-30T13:24:43</datetime>
        </informationbeforedive>
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
        <informationafterdive>
            <diveduration>30</diveduration>
            <greatestdepth>32.2</greatestdepth>
            <lowesttemperature>250.4</lowesttemperature>
        </informationafterdive>
      </dive>
    </repetitiongroup>
  </profiledata>
</uddf>
"""

UDDF_DUMP = b"""\
<?xml version='1.0' encoding='utf-8'?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
  <generator>
    <name>kenozooid</name>
    <version>0.1.0</version>
    <manufacturer>
      <name>Kenozooid Team</name>
      <contact>
        <homepage>http://wrobell.it-zone.org/kenozooid/</homepage>
      </contact>
    </manufacturer>
    <datetime>2010-11-07 21:13:24</datetime>
  </generator>
  <diver>
    <owner>
      <personal>
        <firstname>Anonymous</firstname>
        <lastname>Guest</lastname>
      </personal>
      <equipment>
        <divecomputer id="ostc">
          <model>OSTC</model>
        </divecomputer>
      </equipment>
    </owner>
  </diver>
  <divecomputercontrol>
    <divecomputerdump>
      <link ref="ostc"/>
      <datetime>2010-11-07 21:13:24</datetime>
      <!-- dcdump: '01234567890abcdef' -->
      <dcdump>QlpoOTFBWSZTWZdWXlwAAAAJAH/gPwAgACKMmAAUwAE0xwH5Gis6xNXmi7kinChIS6svLgA=</dcdump>
    </divecomputerdump>
  </divecomputercontrol>
</uddf>
"""

UDDF_BUDDY = b"""\
<?xml version='1.0' encoding='utf-8'?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
<diver>
    <owner>
        <personal>
            <firstname>Anonymous</firstname>
            <lastname>Guest</lastname>
        </personal>
    </owner>
    <buddy id="b1"><personal>
        <firstname>F1 AA</firstname><lastname>L1 X1</lastname>
        <membership memberid="m1" organisation="CFT"/>
    </personal></buddy>
    <buddy id="b2"><personal>
        <firstname>F2 BB</firstname><lastname>L2 Y2</lastname>
        <membership memberid="m2" organisation="CFT"/>
    </personal></buddy>
    <buddy id="b3"><personal>
        <firstname>F3 CC</firstname><lastname>L3 m4</lastname>
        <membership memberid="m3" organisation="PADI"/>
    </personal></buddy>
    <buddy id="b4"><personal>
        <firstname>F4 DD</firstname><lastname>L4 m2</lastname>
        <membership memberid="m4" organisation="PADI"/>
    </personal></buddy>
</diver>
</uddf>
"""

UDDF_SITE = b"""\
<?xml version='1.0' encoding='utf-8'?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
<divesite>
    <site id='markgraf'><name>SMS Markgraf</name><geography><location>Scapa Flow</location></geography></site>
    <site id='konig'><name>SMS Konig</name><geography><location>Scapa Flow</location></geography></site>
</divesite>
</uddf>
"""

def xml2et(data):
    doc = et.XML(''.join(l for l in data))
    sd = et.tostring(doc, pretty_print=True)
    return doc, sd


class FindDataTestCase(unittest.TestCase):
    """
    Data search within UDDF tests.
    """
    def _qt(self, xml, query, expected, **data):
        """
        Execute XPath query and check for expected node with specified id.
        """
        f = BytesIO(xml)
        nodes = query(et.parse(f), **data)
        node = nodes[0]
        self.assertEquals(expected, node.get('id'), nodes)


    def test_xp_first(self):
        """
        Test finding first element using XPath
        """
        doc = et.parse(BytesIO(UDDF_SITE))
        nodes = ku.XPath('//uddf:site')(doc)
        n = ku.xp_first(doc, '//uddf:site')
        self.assertTrue(n is nodes[0])


    def test_xp_last(self):
        """
        Test finding last element using XPath
        """
        doc = et.parse(BytesIO(UDDF_SITE))
        nodes = ku.XPath('//uddf:site')(doc)
        n = ku.xp_last(doc, '//uddf:site')
        self.assertTrue(n is nodes[1])

        
    def test_parsing(self):
        """
        Test basic XML parsing routine
        """
        f = BytesIO(UDDF_PROFILE)
        depths = list(ku.parse(f, '//uddf:waypoint//uddf:depth/text()'))
        self.assertEqual(7, len(depths))

        expected = ['1.48', '2.43', '3.58', '2.61', '4.18', '6.25', '8.32']
        self.assertEqual(expected, depths)


    def test_dive_data(self):
        """
        Test parsing UDDF default dive data
        """
        f = BytesIO(UDDF_PROFILE)
        node = next(ku.parse(f, '//uddf:dive[1]'))
        dive = ku.dive_data(node)
        self.assertEquals(datetime(2009, 9, 19, 13, 10, 23), dive.datetime)
        self.assertEquals(20, dive.duration)
        self.assertEquals(30.2, dive.depth)
        self.assertEquals(251.4, dive.temp)
        self.assertEquals(10.1, dive.avg_depth)


    def test_profile_data(self):
        """
        Test parsing UDDF default dive profile data
        """
        f = BytesIO(UDDF_PROFILE)
        node = next(ku.parse(f, '//uddf:dive[2]'))
        profile = list(ku.dive_profile(node))
        self.assertEquals(4, len(profile))

        self.assertEquals(kd.Sample(depth=2.61, time=0, temp=296.73), profile[0])
        self.assertEquals(kd.Sample(depth=4.18, time=10), profile[1])
        self.assertEquals(kd.Sample(depth=6.25, time=20), profile[2])
        self.assertEquals(kd.Sample(depth=8.32, time=30, temp=297.26), profile[3])


    def test_dump_data(self):
        """
        Test parsing UDDF dive computer dump data
        """
        f = BytesIO(UDDF_DUMP)
        node = next(ku.parse(f, '//uddf:divecomputerdump'))
        dump = ku.dump_data(node)

        expected = ('ostc',
                'OSTC',
                datetime(2010, 11, 7, 21, 13, 24),
                b'01234567890abcdef')
        self.assertEquals(expected, dump)


    def test_dump_data_decode(self):
        """
        Test dive computer data decoding stored in UDDF dive computer dump file
        """
        data = 'QlpoOTFBWSZTWZdWXlwAAAAJAH/gPwAgACKMmAAUwAE0xwH5Gis6xNXmi7kinChIS6svLgA='
        s = ku._dump_decode(data)
        self.assertEquals(b'01234567890abcdef', s)


    def test_site_data(self):
        """
        Test dive site data parsing
        """
        f = BytesIO(UDDF_SITE)
        node = next(ku.parse(f, '//uddf:site[1]'))
        site = ku.site_data(node)
        expected = ('markgraf', 'SMS Markgraf', 'Scapa Flow', None, None)
        self.assertEquals(expected, site)


    def test_buddy_query(self):
        """
        Test buddy XPath query
        """
        # by id and name
        self._qt(UDDF_BUDDY, ku.XP_FIND_BUDDY, 'b1', buddy='b1') # by id
        self._qt(UDDF_BUDDY, ku.XP_FIND_BUDDY, 'b4', buddy='F4') # by firstname
        self._qt(UDDF_BUDDY, ku.XP_FIND_BUDDY, 'b3', buddy='L3') # by lastname

        # by organisation
        self._qt(UDDF_BUDDY, ku.XP_FIND_BUDDY, 'b1', buddy='CFT')
        self._qt(UDDF_BUDDY, ku.XP_FIND_BUDDY, 'b3', buddy='PADI')
        # by organisation membership number
        self._qt(UDDF_BUDDY, ku.XP_FIND_BUDDY, 'b1', buddy='m1')


    def test_site_query(self):
        """
        Test dive site XPath query
        """
        # by id
        self._qt(UDDF_SITE, ku.XP_FIND_SITE, 'konig', site='konig') 

        # by name
        self._qt(UDDF_SITE, ku.XP_FIND_SITE, 'markgraf', site='Markg')

        # by location
        self._qt(UDDF_SITE, ku.XP_FIND_SITE, 'markgraf', site='Scapa Flow')


    def test_version(self):
        """
        Test getting UDDF version
        """
        s1 = b"""\
<uddf xmlns="http://www.streit.cc/uddf/3.0/" version="3.0.0">
</uddf>
"""
        s2 = b"""\
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
</uddf>
"""
        self.assertEquals((3, 0), ku.get_version(BytesIO(s1)))
        self.assertEquals((3, 1), ku.get_version(BytesIO(s2)))



class CreateDataTestCase(unittest.TestCase):
    """
    UDDF creation and saving tests
    """
    def test_create_basic(self):
        """
        Test basic UDDF file creation
        """
        now = datetime.now()

        doc = ku.create(datetime=now)
        self.assertEquals('3.1.0', doc.get('version'))

        q = '//uddf:generator/uddf:datetime/text()'
        dt = ku.xp_first(doc, q)
        self.assertEquals(ku.FMT_DT(now), dt)


    def test_save(self):
        """
        Test UDDF data saving
        """
        doc = ku.create()
        f = BytesIO()
        ku.save(doc, f)
        s = f.getvalue()
        self.assertFalse(b'uddf:' in s)
        f.close() # check if file closing is possible

        preamble = b"""\
<?xml version='1.0' encoding='UTF-8'?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">\
"""
        self.assertTrue(s.startswith(preamble), s)


    def test_set_data(self):
        """
        Test generic method for creating XML data
        """
        doc = et.XML('<uddf><diver></diver></uddf>')
        fq = {
            'fname': 'diver/firstname',
            'lname': 'diver/lastname',
        }
        ku.set_data(doc, fq, fname='A', lname='B')

        sd = et.tostring(doc)

        divers = doc.xpath('//diver')
        self.assertEquals(1, len(divers), sd)
        self.assertTrue(divers[0].text is None, sd)

        fnames = doc.xpath('//firstname/text()')
        self.assertEquals(1, len(fnames), sd)
        self.assertEquals('A', fnames[0], sd)

        lnames = doc.xpath('//lastname/text()')
        self.assertEquals(1, len(lnames), sd)
        self.assertEquals('B', lnames[0], sd)

        # create first name but not last name
        ku.set_data(doc, fq, fname='X')
        sd = et.tostring(doc)

        divers = doc.xpath('//diver')
        self.assertEquals(1, len(divers), sd)
        self.assertTrue(divers[0].text is None, sd)

        fnames = doc.xpath('//firstname/text()')
        self.assertEquals(2, len(fnames), sd)
        self.assertEquals(['A', 'X'], fnames, sd)

        lnames = doc.xpath('//lastname/text()')
        self.assertEquals(1, len(lnames), sd)
        self.assertEquals('B', lnames[0], sd)


    def test_create_data_list(self):
        """
        Test generic method for creating list of XML data
        """
        doc = et.XML('<uddf><diver></diver></uddf>')
        fq = {
            'name': ['diver/firstname', 'diver/lastname'],
            'address': ['diver/street', 'diver/city'],
        }
        ku.set_data(doc, fq, name=['A', 'B'], address=['X', 'Y'])

        sd = et.tostring(doc)

        divers = doc.xpath('//diver')
        self.assertEquals(1, len(divers), sd)
        self.assertTrue(divers[0].text is None, sd)

        fnames = doc.xpath('//firstname/text()')
        self.assertEquals(1, len(fnames), sd)
        self.assertEquals('A', fnames[0], sd)

        lnames = doc.xpath('//lastname/text()')
        self.assertEquals(1, len(lnames), sd)
        self.assertEquals('B', lnames[0], sd)

        streets = doc.xpath('//street/text()')
        self.assertEquals(1, len(streets), sd)
        self.assertEquals('X', streets[0], sd)

        cities = doc.xpath('//city/text()')
        self.assertEquals(1, len(cities), sd)
        self.assertEquals('Y', cities[0], sd)

        # create first name but no last name nor address
        ku.set_data(doc, fq, name=['A1'])
        sd = et.tostring(doc)

        divers = doc.xpath('//diver')
        self.assertEquals(1, len(divers), sd)
        self.assertTrue(divers[0].text is None, sd)

        fnames = doc.xpath('//firstname/text()')
        self.assertEquals(2, len(fnames), sd)
        self.assertEquals(['A', 'A1'], fnames, sd)

        lnames = doc.xpath('//lastname/text()')
        self.assertEquals(1, len(lnames), sd)
        self.assertEquals('B', lnames[0], sd)

        streets = doc.xpath('//street/text()')
        self.assertEquals(1, len(streets), sd)
        self.assertEquals('X', streets[0], sd)

        cities = doc.xpath('//city/text()')
        self.assertEquals(1, len(cities), sd)
        self.assertEquals('Y', cities[0], sd)


    def test_create_attr_data(self):
        """
        Test generic method for creating XML data as attributes
        """
        doc = et.XML('<uddf><diver></diver></uddf>')
        fq = {
            'fname': 'diver/@fn',
            'lname': 'diver/@ln',
        }
        ku.set_data(doc, fq, fname='A1', lname='B1')
        sd = et.tostring(doc)

        divers = doc.xpath('//diver')
        self.assertEquals(2, len(divers), sd)
        self.assertTrue(divers[0].text is None, sd)
        self.assertTrue(divers[1].text is None, sd)

        fnames = doc.xpath('//diver/@fn')
        self.assertEquals(1, len(fnames), sd)
        self.assertEquals('A1', fnames[0], sd)

        lnames = doc.xpath('//diver/@ln')
        self.assertEquals(1, len(lnames), sd)
        self.assertEquals('B1', lnames[0], sd)

        ku.set_data(doc, fq, fname='A2', lname='B2')
        sd = et.tostring(doc)

        divers = doc.xpath('//diver')
        self.assertEquals(3, len(divers), sd)

        fnames = doc.xpath('//diver/@fn')
        self.assertEquals(2, len(fnames), sd)
        self.assertEquals(['A1', 'A2'], fnames, sd)

        lnames = doc.xpath('//diver/@ln')
        self.assertEquals(2, len(lnames), sd)
        self.assertEquals(['B1', 'B2'], lnames, sd)


    def test_create_attr_list_data(self):
        """
        Test generic method for creating list of XML data with attributes
        """
        doc = et.XML('<uddf></uddf>')
        fq = {
            'buddies': ['link/@ref', 'link/@ref'],
        }
        ku.set_data(doc, fq, buddies=['A1', 'A2'])
        sd = et.tostring(doc)

        links = doc.xpath('//link')
        self.assertEquals(2, len(links), sd)
        self.assertEquals('A1', links[0].get('ref'), sd)
        self.assertEquals('A2', links[1].get('ref'), sd)


    def test_create_attr_list_data_reuse(self):
        """
        Test generic method for creating list of XML data in attributes
        with node reuse
        """
        doc = et.XML('<uddf></uddf>')
        fq = {
            's': ['t/@a', 't/@b'],
            't': ['t/@a', 't/@b', 't/@a', 't/@b'],
        }
        ku.set_data(doc, fq, s=[1, 2], t=['A1', 'A2', 'A3', 'A4'])
        sd = et.tostring(doc)

        t = doc.xpath('//t')
        self.assertEquals(3, len(t), sd)
        self.assertEquals('1', t[0].get('a'), sd)
        self.assertEquals('2', t[0].get('b'), sd)
        self.assertEquals('A1', t[1].get('a'), sd)
        self.assertEquals('A2', t[1].get('b'), sd)
        self.assertEquals('A3', t[2].get('a'), sd)
        self.assertEquals('A4', t[2].get('b'), sd)


    def test_create_node(self):
        """
        Test generic method for creating XML nodes
        """
        doc = et.XML('<uddf><diver></diver></uddf>')

        dq = et.XPath('//diver')
        tq = et.XPath('//test')

        d, t = ku.create_node('diver/test')
        self.assertEquals('diver', d.tag)
        self.assertEquals('test', t.tag)

        *_, = ku.create_node('diver/test', parent=doc)
        sd = et.tostring(doc, pretty_print=True)
        self.assertEquals(1, len(dq(doc)), sd)
        self.assertEquals(1, len(tq(doc)), sd)

        *_, = ku.create_node('diver/test', parent=doc)
        sd = et.tostring(doc, pretty_print=True)
        self.assertEquals(1, len(dq(doc)), sd)
        self.assertEquals(2, len(tq(doc)), sd)


    def test_create_node_prepend(self):
        """
        Test generic method for creating XML nodes with prepending
        """
        doc = et.XML('<uddf><diver></diver></uddf>')

        dq = et.XPath('//diver')
        tq = et.XPath('//test1 | //test2')

        d, t = ku.create_node('diver/test2', parent=doc)
        d, t = ku.create_node('diver/test1', parent=doc, append=False)
        sd = et.tostring(doc, pretty_print=True)

        self.assertEquals(1, len(dq(doc)), sd)

        nodes = tq(doc)
        self.assertEquals(2, len(nodes), sd)
        # test order
        self.assertEquals('test1', nodes[0].tag)
        self.assertEquals('test2', nodes[1].tag)


    def test_create_dive_data(self):
        """
        Test dive data creation
        """
        f = ku.create()
        dive = ku.create_dive_data(f, datetime=datetime(2010, 12, 29, 20, 14),
                depth=32.15, duration=2001.0)
        s = et.tostring(f)

        self.assertTrue(ku.xp_first(f, '//uddf:repetitiongroup/@id') is not None)
        self.assertTrue(ku.xp_first(f, '//uddf:dive/@id') is not None)

        d = list(ku.xp(f, '//uddf:dive'))
        self.assertEquals(1, len(d), s)

        d = list(ku.xp(f, '//uddf:dive/uddf:informationbeforedive/uddf:datetime/text()'))
        self.assertEquals(1, len(d), s)
        self.assertEquals('2010-12-29T20:14:00', d[0], s)

        d = list(ku.xp(f, '//uddf:dive/uddf:informationafterdive/uddf:greatestdepth/text()'))
        self.assertEquals(1, len(d), s)
        self.assertEquals('32.1', d[0], s)

        d = list(ku.xp(f, '//uddf:dive/uddf:informationafterdive/uddf:diveduration/text()'))
        self.assertEquals(1, len(d), s)
        self.assertEquals('2001', d[0], s)

        # create 2nd dive
        dive = ku.create_dive_data(f, datetime=datetime(2010, 12, 30, 20, 14),
                depth=32.15, duration=2001.0)
        s = et.tostring(f, pretty_print=True)
        d = list(ku.xp(f, '//uddf:dive'))
        self.assertEquals(2, len(d), s)

        dt = tuple(ku.xp(f, '//uddf:dive/uddf:informationbeforedive/uddf:datetime/text()'))
        expected = '2010-12-29T20:14:00', '2010-12-30T20:14:00'
        self.assertEquals(expected, dt, s)


    def test_create_dive_data_with_dive_site(self):
        """
        Test dive data creation with dive site
        """
        doc = ku.create()
        ku.create_site_data(doc, id='markgraf', name='SMS Markgraf',
                location='Scapa Flow')
        dive = ku.create_dive_data(doc, datetime=datetime(2010, 12, 29, 20, 14),
                depth=32.15, duration=2001.0, site='markgraf')
        s = et.tostring(doc, pretty_print=True)

        site_id = ku.xp_first(dive, './uddf:informationbeforedive/uddf:link/@ref')
        self.assertEquals('markgraf', site_id, s)

        f = BytesIO()
        ku.save(doc, f) # validate created UDDF


    def test_create_dive_data_with_buddy(self):
        """
        Test dive data creation with buddy data
        """
        doc = ku.create()
        ku.create_buddy_data(doc, id='b1', fname='BF1', lname='BL1')
        ku.create_buddy_data(doc, id='b2', fname='BF2', lname='BL2')
        dive = ku.create_dive_data(doc, datetime=datetime(2010, 12, 29, 20, 14),
                depth=32.15, duration=2001.0, buddies=('b1', 'b2'))
        s = et.tostring(doc, pretty_print=True)

        b1, b2 = ku.xp(dive, './uddf:informationbeforedive/uddf:link/@ref')
        self.assertEquals('b1', b1, s)
        self.assertEquals('b2', b2, s)

        f = BytesIO()
        ku.save(doc, f) # validate created UDDF


    def test_create_dc_data(self):
        """
        Test creating dive computer information data in UDDF file
        """
        n = ku.create_dc_data('tid', model='Test 1')
        doc, sd = xml2et(ku.create_uddf(equipment=n))

        r = ku.xp_first(doc, '//uddf:owner//uddf:divecomputer/@id')
        self.assertEquals(r, 'tid', sd)

        r = ku.xp_first(doc, '//uddf:owner//uddf:divecomputer/uddf:model/text()')
        self.assertEquals(r, 'Test 1', sd)

        # name is the same as model
        r = ku.xp_first(doc, '//uddf:owner//uddf:divecomputer/uddf:name/text()')
        self.assertEquals(r, 'Test 1', sd)


    def test_create_dive_samples(self):
        """
        Test UDDF dive profile sample creation
        """
        s = kd.Sample(depth=3.1, time=19, temp=20),
        samples = ku.create_dive_samples(s)
        n, sd = xml2et(xml.dive(samples))
        self.assertEquals('19', ku.xp_first(n, '//divetime/text()'), sd)
        self.assertEquals('3.1', ku.xp_first(n, '//depth/text()'), sd)
        self.assertEquals('20.0', ku.xp_first(n, '//temperature/text()'), sd)


    def test_create_dive_samples_deco_alarm(self):
        """
        Test UDDF dive profile sample creation with deco alarm
        """
        s = kd.Sample(depth=3.1, time=19, temp=20, alarm=('deco',)),
        samples = ku.create_dive_samples(s)
        n, sd = xml2et(xml.dive(samples))
        self.assertEquals('deco', ku.xp_first(n, '//alarm/text()'), sd)


    def test_create_dive_samples_setpoint(self):
        """
        Test UDDF dive profile sample creation with setpoint
        """
        s = kd.Sample(depth=3.1, time=19, temp=20, setpoint=1.17,
                setpointby='user'),
        samples = ku.create_dive_samples(s)
        n, sd = xml2et(xml.dive(samples))
        self.assertEquals('1.17', ku.xp_first(n, '//setpo2/text()'), sd)
        self.assertEquals('user', ku.xp_first(n, '//setpo2/@setby'), sd)
        

    def test_dump_data_encode(self):
        """
        Test dive computer data encoding to be stored in UDDF dive computer dump file
        """
        s = ku._dump_encode(b'01234567890abcdef')
        self.assertEquals(b'QlpoOTFBWSZTWZdWXlwAAAAJAH/gPwAgACKMmAAUwAE0xwH5Gis6xNXmi7kinChIS6svLgA=', s)


    def test_create_site(self):
        """
        Test creating dive site data
        """
        f = ku.create()
        site = ku.create_site_data(f, id='markgraf', name='SMS Markgraf',
                location='Scapa Flow')
        s = et.tostring(f, pretty_print=True)

        d = list(ku.xp(f, '//uddf:site'))
        self.assertEquals(1, len(d), s)

        id = ku.xp_first(f, '//uddf:site/@id')
        self.assertEquals('markgraf', id, s)

        d = list(ku.xp(f, '//uddf:site/uddf:geography'))
        self.assertEquals(1, len(d), s)

        d = list(ku.xp(f, '//uddf:site/uddf:geography/uddf:location/text()'))
        self.assertEquals(1, len(d), s)
        self.assertEquals('Scapa Flow', d[0], s)

        # create 2nd dive site
        site = ku.create_site_data(f, id='konig', name='SMS Konig',
                location='Scapa Flow')
        s = et.tostring(f, pretty_print=True)
        d = list(ku.xp(f, '//uddf:site'))
        self.assertEquals(2, len(d), s)

        ids = list(ku.xp(f, '//uddf:site/@id'))
        self.assertEquals(['markgraf', 'konig'], ids, s)


    def test_create_site_with_pos(self):
        """
        Test creating dive site data with position
        """
        f = ku.create()
        buddy = ku.create_site_data(f, name='SMS Konig', location='Scapa Flow',
                x=6.1, y=6.2)
        s = et.tostring(f, pretty_print=True)

        x = ku.xp_first(f, '//uddf:site//uddf:longitude/text()')
        self.assertEquals(6.1, float(x))
        y = ku.xp_first(f, '//uddf:site//uddf:latitude/text()')
        self.assertEquals(6.2, float(y))


    def test_create_site_no_id(self):
        """
        Test creating dive site data with autogenerated id
        """
        f = ku.create()
        buddy = ku.create_site_data(f, name='Konig', location='Scapa Flow')
        s = et.tostring(f, pretty_print=True)

        id = ku.xp_first(f, '//uddf:site/@id')
        self.assertTrue(id is not None, s)


    def test_create_buddy(self):
        """
        Test creating buddy data
        """
        f = ku.create()
        buddy = ku.create_buddy_data(f, id='tcora',
                fname='Thomas', mname='Henry', lname='Corra',
                org='CFT', number='123')
        s = et.tostring(f)

        d = list(ku.xp(f, '//uddf:buddy'))
        self.assertEquals(1, len(d), s)

        id = ku.xp_first(f, '//uddf:buddy/@id')
        self.assertEquals('tcora', id, s)

        d = list(ku.xp(f, '//uddf:buddy/uddf:personal/uddf:firstname/text()'))
        self.assertEquals(1, len(d), s)
        self.assertEquals('Thomas', d[0], s)

        d = list(ku.xp(f, '//uddf:buddy/uddf:personal/uddf:middlename/text()'))
        self.assertEquals(1, len(d), s)
        self.assertEquals('Henry', d[0], s)

        d = list(ku.xp(f, '//uddf:buddy/uddf:personal/uddf:lastname/text()'))
        self.assertEquals(1, len(d), s)
        self.assertEquals('Corra', d[0], s)

        d = list(ku.xp(f, '//uddf:buddy/uddf:personal/uddf:membership'))
        self.assertEquals(1, len(d), s)

        d = list(ku.xp(f,
            '//uddf:buddy/uddf:personal/uddf:membership/@organisation'))
        self.assertEquals('CFT', d[0], s)

        d = list(ku.xp(f,
            '//uddf:buddy/uddf:personal/uddf:membership/@memberid'))
        self.assertEquals('123', d[0], s)

        # create 2nd buddy
        buddy = ku.create_buddy_data(f, id='tcora2',
                fname='Thomas', mname='Henry', lname='Corra',
                org='CFT', number='123')
        s = et.tostring(f, pretty_print=True)
        d = list(ku.xp(f, '//uddf:buddy'))
        self.assertEquals(2, len(d), s)

        ids = list(ku.xp(f, '//uddf:buddy/@id'))
        self.assertEquals(['tcora', 'tcora2'], ids, s)


    def test_create_buddy_no_id(self):
        """
        Test creating buddy data with autogenerated id
        """
        f = ku.create()
        buddy = ku.create_buddy_data(f,
                fname='Thomas', mname='Henry', lname='Corra',
                org='CFT', number='123')
        s = et.tostring(f, pretty_print=True)

        id = ku.xp_first(f, '//uddf:buddy/@id')
        self.assertTrue(id is not None, s)


class NodeRemovalTestCase(unittest.TestCase):
    """
    Node removal tests.
    """
    def test_node_removal(self):
        """
        Test node removal
        """
        f = BytesIO(UDDF_BUDDY)
        doc = et.parse(f)
        buddy = ku.XP_FIND_BUDDY(doc, buddy='m1')[0]
        p = buddy.getparent()

        assert buddy in p
        assert len(p) == 5 # the owner and 4 buddies

        ku.remove_nodes(doc, ku.XP_FIND_BUDDY, buddy='m1')
        self.assertEquals(4, len(p))
        self.assertFalse(buddy in p, et.tostring(doc, pretty_print=True))



class PostprocessingTestCase(unittest.TestCase):
    """
    UDDF postprocessing tests.
    """
    def test_reorder(self):
        """
        Test UDDF reordering
        """
        doc = et.parse(BytesIO(b"""
<uddf xmlns="http://www.streit.cc/uddf/3.1/">
<generator>
    <name>kenozooid</name>
</generator>
<diver>
    <owner id='owner'>
        <personal>
            <firstname>Anonymous</firstname>
            <lastname>Guest</lastname>
        </personal>
    </owner>
</diver>
<profiledata>
<repetitiongroup id='r1'>
<dive id='d1'>
    <informationbeforedive>
        <datetime>2009-03-02T23:02:00</datetime>
    </informationbeforedive>
    <informationafterdive>
        <diveduration>20</diveduration>
        <greatestdepth>30.2</greatestdepth>
        <lowesttemperature>251.4</lowesttemperature>
    </informationafterdive>
</dive>
<dive id='d2'>
    <informationbeforedive>
        <datetime>2009-04-02T23:02:00</datetime>
    </informationbeforedive>
    <informationafterdive>
        <diveduration>20</diveduration>
        <greatestdepth>30.2</greatestdepth>
        <lowesttemperature>251.4</lowesttemperature>
    </informationafterdive>
</dive>
<dive id='d3'>
    <informationbeforedive>
        <datetime>2009-04-02T23:02:00</datetime>
    </informationbeforedive>
    <informationafterdive>
        <diveduration>20</diveduration>
        <greatestdepth>30.2</greatestdepth>
        <lowesttemperature>251.4</lowesttemperature>
    </informationafterdive>
</dive>
<dive id='d4'>
    <informationbeforedive>
        <datetime>2009-03-02T23:02:00</datetime>
    </informationbeforedive>
    <informationafterdive>
        <diveduration>20</diveduration>
        <greatestdepth>30.2</greatestdepth>
        <lowesttemperature>251.4</lowesttemperature>
    </informationafterdive>
</dive>
</repetitiongroup>
<repetitiongroup id='r2'> <!-- one more repetition group; it shall be removed -->
<dive id='d5'>
    <informationbeforedive>
        <datetime>2009-03-02T23:02:00</datetime>
    </informationbeforedive>
    <informationafterdive>
        <diveduration>20</diveduration>
        <greatestdepth>30.2</greatestdepth>
        <lowesttemperature>251.4</lowesttemperature>
    </informationafterdive>
</dive>
</repetitiongroup>
</profiledata>
</uddf>
"""))
        ku.reorder(doc)

        nodes = list(ku.xp(doc, '//uddf:repetitiongroup'))
        self.assertEquals(1, len(nodes))
        self.assertTrue(nodes[0].get('id') is not None)
        nodes = list(ku.xp(doc, '//uddf:dive'))
        self.assertEquals(2, len(nodes))

        # check the order of dives
        times = list(ku.xp(doc, '//uddf:dive/uddf:informationbeforedive/uddf:datetime/text()'))
        self.assertEquals(['2009-03-02T23:02:00', '2009-04-02T23:02:00'], times)



class NodeRangeTestCase(unittest.TestCase):
    """
    Node range tests.
    """
    def test_simple(self):
        """
        Test parsing simple numerical ranges
        """
        self.assertEquals('1 <= position() and position() <= 3',
                ku.node_range('1-3'))
        self.assertEquals('position() = 2 or position() = 4',
                ku.node_range('2, 4'))
        self.assertEquals('position() = 1 or position() = 3'
                ' or 4 <= position() and position() <= 7',
            ku.node_range('1,3,4-7'))
        self.assertEquals('1 <= position()', ku.node_range('1-'))
        self.assertEquals('position() <= 10', ku.node_range('-10'))


    def test_errors(self):
        """
        Test invalid ranges
        """
        self.assertRaises(ku.RangeError, ku.node_range, '30--')
        self.assertRaises(ku.RangeError, ku.node_range, '30-2-')
        self.assertRaises(ku.RangeError, ku.node_range, '1,a,2')
        self.assertRaises(ku.RangeError, ku.node_range, '1-a,3')



class NodeCopyTestCase(unittest.TestCase):
    """
    Node copying tests.
    """
    def test_simple_copy(self):
        """
        Test simple UDDF node copy
        """
        SOURCE = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <a1>
        <a2/>
        <a2/>
    </a1>
    <b1>
        <b2/>
    </b1>
</uddf>
"""
        TARGET = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <c/>
</uddf>
"""
        s = BytesIO(SOURCE)
        a, *_ = ku.parse(s, '//uddf:a1')

        t = et.XML(TARGET)
        c = ku.xp_first(t, '//uddf:c')

        r = ku.copy(a, c)
        self.assertEquals('{http://www.streit.cc/uddf/3.1/}a1', r.tag)

        n = ku.xp_first(t, '//uddf:a1')
        self.assertTrue(n is not None)
        self.assertEquals(2, len(n))


    def test_copy_ref_descendant_nodes(self):
        """
        Test copying UDDF node with descendants referencing themselves
        """
        SOURCE = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <a1>
        <a2 id = 'id-a1'/>
        <a2 id = 'id-a2' ref = 'id-a1'/>
    </a1>
    <b1>
        <b2/>
    </b1>
</uddf>
"""
        TARGET = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <c/>
</uddf>
"""
        s = BytesIO(SOURCE)
        a, *_ = ku.parse(s, '//uddf:a1')

        t = et.XML(TARGET)
        c = ku.xp_first(t, '//uddf:c')

        ku.copy(a, c)

        n = ku.xp_first(t, '//uddf:a1')
        self.assertTrue(n is not None)
        self.assertEquals(2, len(n))


    def test_copy_ref_nodes(self):
        """
        Test copying UDDF node referencing other nodes
        """
        SOURCE = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <a1>
        <a2 id = 'id-a1'/>
        <a2 id = 'id-a2' ref = 'id-b2'/>
    </a1>
    <b1>
        <b2 id = 'id-b2'/>
    </b1>
</uddf>
"""
        TARGET = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <c/>
    <b1>
        <b2 id = 'id-b2'/>
    </b1>
</uddf>
"""
        s = BytesIO(SOURCE)
        a, *_ = ku.parse(s, '//uddf:a1')

        t = et.XML(TARGET)
        c = ku.xp_first(t, '//uddf:c')

        ku.copy(a, c)
        sd = et.tostring(t, pretty_print=True)

        n = ku.xp_first(t, '//uddf:a1')
        self.assertTrue(n is not None, sd)

        self.assertEquals(2, len(n), sd)
        self.assertEquals('id-a1', n[0].get('id'))
        self.assertEquals('id-a2', n[1].get('id'))


    def test_copy_ref_nodes_non_existing(self):
        """
        Test copying UDDF node referencing missing node
        """
        SOURCE = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <a1>
        <a2 id = 'id-a1'/>
        <a2 id = 'id-a2' ref = 'id-b1'/>
    </a1>
    <b1>
        <b2/>
    </b1>
</uddf>
"""
        TARGET = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <c/>
</uddf>
"""
        s = BytesIO(SOURCE)
        a, *_ = ku.parse(s, '//uddf:a1')

        t = et.XML(TARGET)
        c = ku.xp_first(t, '//uddf:c')

        ku.copy(a, c)

        n = ku.xp_first(t, '//uddf:a1')
        self.assertTrue(n is not None)
        self.assertEquals(1, len(n))
        self.assertEquals('id-a1', n[0].get('id'))


    def test_copy_mref_nodes_non_existing(self):
        """
        Test copying UDDF multiple nodes referencing missing node
        """
        SOURCE = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <a1>
        <a2 id = 'id-a21'/>
        <a2 id = 'id-a22' ref = 'id-b1'/>
        <a2 id = 'id-a23' ref = 'id-b1'/>
        <a2 id = 'id-a24'/>
    </a1>
    <b1>
        <b2/>
    </b1>
</uddf>
"""
        TARGET = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <c/>
</uddf>
"""
        s = BytesIO(SOURCE)
        a, *_ = ku.parse(s, '//uddf:a1')

        t = et.XML(TARGET)
        c = ku.xp_first(t, '//uddf:c')

        ku.copy(a, c)
        sd = et.tostring(t, pretty_print=True)

        n = ku.xp_first(t, '//uddf:a1')
        self.assertTrue(n is not None, sd)
        self.assertEquals(2, len(n), sd)
        self.assertEquals('id-a21', n[0].get('id'), sd)
        self.assertEquals('id-a24', n[1].get('id'), sd)


    def test_removal_on_empty_parent(self):
        """
        Test removal of empty UDDF parent node on copying
        """
        SOURCE = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <a1>
        <a3 id = 'id-a3'>
            <a5 id = 'id-a5'>
                <a2 id = 'id-a21' ref = 'id-b1'/>
                <a2 id = 'id-a22' ref = 'id-b1'/>
            </a5>
        </a3>
        <a4 id = 'id-a4'/>
    </a1>
    <b1>
        <b2/>
    </b1>
</uddf>
"""
        TARGET = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <c/>
</uddf>
"""
        s = BytesIO(SOURCE)
        a, *_ = ku.parse(s, '//uddf:a1')

        t = et.XML(TARGET)
        c = ku.xp_first(t, '//uddf:c')

        ku.copy(a, c)
        sd = et.tostring(t, pretty_print=True)

        # a2 nodes are removed
        # a3 is removed as empty parent node
        # a4 is left
        self.assertTrue(ku.xp_first(t, '//uddf:a2') is None, sd)
        self.assertTrue(ku.xp_first(t, '//uddf:a3') is None, sd)

        n = ku.xp_first(t, '//uddf:a1')
        self.assertTrue(n is not None, sd)
        self.assertEquals(1, len(n), sd)
        self.assertEquals('id-a4', n[0].get('id'), sd)


    def test_removal_on_empty_ref_parent(self):
        """
        Test removal of empty UDDF referencing parent node on copying
        """
        SOURCE = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <a1>
        <a3 id = 'id-a3'>
            <a5 id = 'id-a5' ref = 'id-b2'>
                <a2 id = 'id-a21' ref = 'id-b1'/>
                <a2 id = 'id-a22' ref = 'id-b1'/>
            </a5>
        </a3>
        <a4 id = 'id-a4'/>
    </a1>
    <b1>
        <b2/>
    </b1>
</uddf>
"""
        TARGET = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <c/>
</uddf>
"""
        s = BytesIO(SOURCE)
        a, *_ = ku.parse(s, '//uddf:a1')

        t = et.XML(TARGET)
        c = ku.xp_first(t, '//uddf:c')

        ku.copy(a, c)
        sd = et.tostring(t, pretty_print=True)

        # a2 nodes are removed
        # a3 is removed as empty parent node
        # a4 is left
        self.assertTrue(ku.xp_first(t, '//uddf:a2') is None, sd)
        self.assertTrue(ku.xp_first(t, '//uddf:a3') is None, sd)

        n = ku.xp_first(t, '//uddf:a1')
        self.assertTrue(n is not None, sd)
        self.assertEquals(1, len(n), sd)
        self.assertEquals('id-a4', n[0].get('id'), sd)


    def test_error_on_empty_copy(self):
        """
        Test error on empty copy
        """
        SOURCE = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <a1 ref = 'id-b1'>
        <a2 ref = 'id-b2'/>
    </a1>
    <b1>
        <b2/>
    </b1>
</uddf>
"""
        TARGET = b"""\
<?xml version="1.0" encoding="utf-8"?>
<uddf xmlns="http://www.streit.cc/uddf/3.1/" version="3.1.0">
    <c/>
</uddf>
"""
        s = BytesIO(SOURCE)
        a, *_ = ku.parse(s, '//uddf:a1')

        t = et.XML(TARGET)
        c = ku.xp_first(t, '//uddf:c')

        self.assertRaises(ValueError, ku.copy, a, c)
        self.assertTrue(ku.xp_first(t, '//uddf:c') is not None)


# vim: sw=4:et:ai
