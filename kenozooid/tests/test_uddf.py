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

from lxml import etree as et
from io import BytesIO
from datetime import datetime
from functools import partial
import unittest

import kenozooid.uddf as ku


UDDF_PROFILE = b"""\
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

UDDF_DUMP = b"""\
<?xml version='1.0' encoding='utf-8'?>
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
          <model>OSTC Mk.1</model>
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
<uddf xmlns="http://www.streit.cc/uddf" version="3.0.0">
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
        <membership memberid="m3" organisation="CFT"/>
    </personal></buddy>
    <buddy id="b4"><personal>
        <firstname>F4 DD</firstname><lastname>L4 m2</lastname>
        <membership memberid="m4" organisation="CFT"/>
    </personal></buddy>
</diver>
</uddf>
"""

UDDF_SITE = b"""\
<?xml version='1.0' encoding='utf-8'?>
<uddf xmlns="http://www.streit.cc/uddf" version="3.0.0">
<divesite>
    <site id='markgraf'><name>SMS Markgraf</name><geography><location>Scapa Flow</location></geography></site>
    <site id='konig'><name>SMS Konig</name><geography><location>Scapa Flow</location></geography></site>
</divesite>
</uddf>
"""


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

        
    def test_parsing(self):
        """
        Test basic XML parsing routine"""
        f = BytesIO(UDDF_PROFILE)
        depths = list(ku.parse(f, '//uddf:waypoint//uddf:depth/text()'))
        self.assertEqual(7, len(depths))

        expected = ['1.48', '2.43', '3.58', '2.61', '4.18', '6.25', '8.32']
        self.assertEqual(expected, depths)


    def test_dive_data(self):
        """
        Test parsing UDDF default dive data"""
        f = BytesIO(UDDF_PROFILE)
        node = next(ku.parse(f, '//uddf:dive[1]'))
        dive = ku.dive_data(node)
        self.assertEquals(datetime(2009, 9, 19, 13, 10, 23), dive.time)


    def test_profile_data(self):
        """
        Test parsing UDDF default dive profile data"""
        f = BytesIO(UDDF_PROFILE)
        node = next(ku.parse(f, '//uddf:dive[2]'))
        profile = list(ku.dive_profile(node))
        self.assertEquals(4, len(profile))

        self.assertEquals((0, 2.61, 296.73), profile[0])
        self.assertEquals((10, 4.18, None), profile[1])
        self.assertEquals((20, 6.25, None), profile[2])
        self.assertEquals((30, 8.32, 297.26), profile[3])


    def test_dump_data(self):
        """
        Test parsing UDDF dive computer dump data"""
        f = BytesIO(UDDF_DUMP)
        node = next(ku.parse(f, '//uddf:divecomputerdump'))
        dump = ku.dump_data(node)

        expected = ('ostc',
                'OSTC Mk.1',
                datetime(2010, 11, 7, 21, 13, 24),
                b'01234567890abcdef')
        self.assertEquals(expected, dump)


    def test_dump_data_decode(self):
        """
        Test dive computer data decoding stored in UDDF dive computer dump file.
        """
        data = 'QlpoOTFBWSZTWZdWXlwAAAAJAH/gPwAgACKMmAAUwAE0xwH5Gis6xNXmi7kinChIS6svLgA='
        s = ku._dump_decode(data)
        self.assertEquals(b'01234567890abcdef', s)


    def test_buddy_query(self):
        """
        Test buddy XPath query.
        """
        self._qt(UDDF_BUDDY, ku.XP_FIND_BUDDY, 'b1', buddy='b1') # by id
        self._qt(UDDF_BUDDY, ku.XP_FIND_BUDDY, 'b1', buddy='m1') # by organisation member number
        self._qt(UDDF_BUDDY, ku.XP_FIND_BUDDY, 'b4', buddy='F4') # by firstname
        self._qt(UDDF_BUDDY, ku.XP_FIND_BUDDY, 'b3', buddy='L3') # by lastname


    def test_site_query(self):
        """
        Test dive site XPath query.
        """
        self._qt(UDDF_SITE, ku.XP_FIND_SITE, 'konig', site='konig') # by id
        self._qt(UDDF_SITE, ku.XP_FIND_SITE, 'markgraf', site='Markg') # by name



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
        self.assertEquals('3.0.0', doc.get('version'))

        q = '//uddf:generator/uddf:datetime/text()'
        dt = doc.xpath(q, namespaces=ku._NSMAP)
        self.assertEquals(now.strftime(ku.FMT_DATETIME), dt[0])


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
<?xml version='1.0' encoding='utf-8'?>
<uddf xmlns="http://www.streit.cc/uddf" version="3.0.0">\
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


    def test_create_attr_data(self):
        """
        Test generic method for creating XML data as attributes
        """
        doc = et.XML('<uddf><diver></diver></uddf>')
        fq = {
            'fname': 'diver/@fn',
            'lname': 'diver/@ln',
        }
        ku.set_data(doc, fq, fname='A', lname='B')

        sd = et.tostring(doc)

        divers = doc.xpath('//diver')
        self.assertEquals(1, len(divers), sd)
        self.assertTrue(divers[0].text is None, sd)

        fnames = doc.xpath('//diver/@fn')
        self.assertEquals(1, len(fnames), sd)
        self.assertEquals('A', fnames[0], sd)

        lnames = doc.xpath('//diver/@ln')
        self.assertEquals(1, len(lnames), sd)
        self.assertEquals('B', lnames[0], sd)



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

        list(ku.create_node('diver/test', parent=doc))
        sd = et.tostring(doc, pretty_print=True)
        self.assertEquals(1, len(dq(doc)), sd)
        self.assertEquals(1, len(tq(doc)), sd)

        list(ku.create_node('diver/test', parent=doc))
        sd = et.tostring(doc, pretty_print=True)
        self.assertEquals(1, len(dq(doc)), sd)
        self.assertEquals(1, len(tq(doc)), sd)

        list(ku.create_node('diver/test', parent=doc, multiple=True))
        sd = et.tostring(doc, pretty_print=True)
        self.assertEquals(1, len(dq(doc)), sd)
        self.assertEquals(2, len(tq(doc)), sd)


    def test_create_dc_data(self):
        """
        Test creating dive computer information data in UDDF file
        """
        doc = ku.create()
        xpath = partial(doc.xpath, namespaces=ku._NSMAP)
        owner = xpath('//uddf:owner')[0]

        ku.create_dc_data(owner, dc_model='Test 1')
        sd = et.tostring(doc, pretty_print=True)

        id_q = '//uddf:owner//uddf:divecomputer/@id'
        ids = xpath(id_q)
        self.assertEquals(1, len(ids), sd)
        self.assertEquals('id206a9b642b3e16c89a61696ab28f3d5c', ids[0], sd)

        model_q = '//uddf:owner//uddf:divecomputer/uddf:model/text()'
        models = xpath(model_q)
        self.assertEquals('Test 1', models[0], sd)

        # update again with the same model
        ku.create_dc_data(owner, dc_model='Test 1')
        sd = et.tostring(doc, pretty_print=True)
        ids = xpath(id_q)
        self.assertEquals(1, len(ids), sd)

        # add different model
        ku.create_dc_data(owner, dc_model='Test 2')
        sd = et.tostring(doc, pretty_print=True)

        eqs = xpath('//uddf:equipment')
        self.assertEquals(1, len(eqs), sd)

        ids = xpath(id_q)
        self.assertEquals(2, len(ids), sd)
        expected = ['id206a9b642b3e16c89a61696ab28f3d5c',
                'id605e79544a68819ce664c088aba92658']
        self.assertEquals(expected, ids, sd)

        models = xpath(model_q)
        expected = ['Test 1', 'Test 2']
        self.assertEquals(expected, models, sd)


    def test_create_dive_profile_sample_default(self):
        """
        Test UDDF dive profile default sample creation
        """
        w = ku.create_dive_profile_sample(None, depth=3.1, time=19, temp=20)
        s = et.tostring(w)
        self.assertEquals('19', ku.xp_first(w, 'uddf:divetime/text()'), s)
        self.assertEquals('3.1', ku.xp_first(w, 'uddf:depth/text()'), s)
        self.assertEquals('20.0', ku.xp_first(w, 'uddf:temperature/text()'), s)


    def test_create_dive_profile_sample_custom(self):
        """
        Test UDDF dive profile custom sample creation
        """
        Q = {
            'depth': 'uddf:depth',
            'time': 'uddf:divetime',
            'temp': 'uddf:temperature',
            'alarm': 'uddf:alarm',
        }
        w = ku.create_dive_profile_sample(None, queries=Q,
                depth=3.1, time=19, temp=20, alarm='deco')
        s = et.tostring(w)
        self.assertEquals('19', ku.xp_first(w, 'uddf:divetime/text()'), s)
        self.assertEquals('3.1', ku.xp_first(w, 'uddf:depth/text()'), s)
        self.assertEquals('20.0', ku.xp_first(w, 'uddf:temperature/text()'), s)
        self.assertEquals('deco', ku.xp_first(w, 'uddf:alarm/text()'), s)
        

    def test_dump_data_encode(self):
        """
        Test dive computer data encoding to be stored in UDDF dive computer dump file
        """
        s = ku._dump_encode('01234567890abcdef')
        self.assertEquals(b'QlpoOTFBWSZTWZdWXlwAAAAJAH/gPwAgACKMmAAUwAE0xwH5Gis6xNXmi7kinChIS6svLgA=', s)


    def test_create_site(self):
        """
        Test creating dive site data
        """
        f = ku.create()
        buddy = ku.create_site_data(f, id='markgraf', name='SMS Markgraf',
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
        buddy = ku.create_site_data(f, id='konig', name='SMS Konig',
                location='Scapa Flow')
        s = et.tostring(f, pretty_print=True)
        d = list(ku.xp(f, '//uddf:site'))
        self.assertEquals(2, len(d), s)

        ids = list(ku.xp(f, '//uddf:site/@id'))
        self.assertEquals(['markgraf', 'konig'], ids, s)


    def test_create_site_with_pos(self):
        """
        Test creating dive site data with position.
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
        Test creating dive site data with autogenerated id.
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

        f = BytesIO()
        ku.save(doc.getroot(), f)

        f = BytesIO(f.getvalue())

        nodes = list(ku.parse(f, '//uddf:repetitiongroup'))
        self.assertEquals(1, len(nodes))
        nodes = list(ku.parse(f, '//uddf:dive'))
        self.assertEquals(2, len(nodes))

        # check the order of dives
        times = list(ku.parse(f, '//uddf:dive/uddf:datetime/text()'))
        self.assertEquals(['2009-03-02 23:02', '2009-04-02 23:02'], times)



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


# vim: sw=4:et:ai
