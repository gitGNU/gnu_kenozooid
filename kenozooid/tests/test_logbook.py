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
Logbook tests.
"""

import shutil
import tempfile
from datetime import datetime
from io import BytesIO
import unittest

import kenozooid.logbook as kl
import kenozooid.uddf as ku
import kenozooid.data as kd
import kenozooid.tests.test_uddf as ktu

class IntegrationTestCaseBase(unittest.TestCase):
    """
    Base class for file based integration tests.
    """
    def setUp(self):
        """
        Create temporary directory to store test files.
        """
        self.tdir = tempfile.mkdtemp()


    def tearDown(self):
        """
        Destroy temporary directory with test files.
        """
        shutil.rmtree(self.tdir)



class DiveAddingIntegrationTestCase(IntegrationTestCaseBase):
    """
    Dive adding integration tests.
    """
    def test_dive_add(self):
        """
        Test adding dive with time, depth and duration
        """
        f = '{}/dive_add.uddf'.format(self.tdir)

        d = kd.Dive(datetime=datetime(2010, 1, 2, 5, 7), depth=33.0,
                duration=3540)
        kl.add_dive(d, f)
        nodes = ku.find(f, '//uddf:dive')

        dn = next(nodes)
        self.assertTrue(next(nodes, None) is None)

        self.assertEquals('2010-01-02T05:07:00',
            ku.xp_first(dn, './/uddf:datetime/text()'))
        self.assertEquals('33.0',
            ku.xp_first(dn, './/uddf:greatestdepth/text()'))
        self.assertEquals('3540',
            ku.xp_first(dn, './/uddf:diveduration/text()'))


    def test_dive_add_with_site(self):
        """
        Test adding dive with time, depth, duration and dive site
        """
        f = '{}/dive_add_site.uddf'.format(self.tdir)

        doc = ku.create()
        ku.create_site_data(doc, id='s1', location='L1', name='N1')
        ku.save(doc, f)

        d = kd.Dive(datetime=datetime(2010, 1, 2, 5, 7), depth=33.0,
                duration=3102)
        kl.add_dive(d, f, qsite='s1')

        nodes = ku.find(f, '//uddf:dive')
        dn = next(nodes)
        self.assertEquals('s1', ku.xp_first(dn, './/uddf:link/@ref'))


    def test_dive_add_with_buddy(self):
        """
        Test adding dive with time, depth, duration and buddy
        """
        f = '{}/dive_add_buddy.uddf'.format(self.tdir)

        doc = ku.create()
        ku.create_buddy_data(doc, id='b1', fname='F', lname='N');
        ku.save(doc, f)

        d = kd.Dive(datetime=datetime(2010, 1, 2, 5, 7), depth=33.0,
                duration=3540)
        kl.add_dive(d, f, qbuddies=['b1'])

        nodes = ku.find(f, '//uddf:dive')
        dn = next(nodes)
        self.assertEquals('b1', ku.xp_first(dn, './/uddf:link/@ref'))


    def test_dive_add_with_buddies(self):
        """
        Test adding dive with time, depth, duration and two buddies
        """
        f = '{}/dive_add_buddy.uddf'.format(self.tdir)

        doc = ku.create()
        ku.create_buddy_data(doc, id='b1', fname='F', lname='N');
        ku.create_buddy_data(doc, id='b2', fname='F', lname='N');
        ku.save(doc, f)

        d = kd.Dive(datetime=datetime(2010, 1, 2, 5, 7), depth=33.0,
                duration=5901)
        kl.add_dive(d, f, qbuddies=['b1', 'b2'])

        nodes = ku.find(f, '//uddf:dive')
        dn = next(nodes)
        self.assertEquals(('b1', 'b2'), tuple(ku.xp(dn, './/uddf:link/@ref')))



class DiveCopyingIntegrationTestCase(IntegrationTestCaseBase):
    """
    Dive copying integration tests.
    """
    def setUp(self):
        """
        Prepare input file.
        """
        super().setUp()
        fin = self.fin = '{}/dive_copy_in.uddf'.format(self.tdir)
        f = open(fin, 'wb')
        f.write(ktu.UDDF_PROFILE)
        f.close()


    def test_dive_copy(self):
        """
        Test copying dive
        """
        fl = '{}/dive_copy_logbook.uddf'.format(self.tdir)

        kl.copy_dives([self.fin], ['1'], None, fl)
        nodes = ku.find(fl, '//uddf:dive')

        dn = next(nodes)
        self.assertTrue(next(nodes, None) is None)

        self.assertEquals('2009-09-19T13:10:23',
            ku.xp_first(dn, './/uddf:datetime/text()'))
        self.assertEquals('30.2',
            ku.xp_first(dn, './/uddf:greatestdepth/text()'))
        self.assertEquals('20',
            ku.xp_first(dn, './/uddf:diveduration/text()'))


    def test_dive_copy_existing(self):
        """
        Test copying existing dive
        """
        fl = '{}/dive_copy_logbook.uddf'.format(self.tdir)
        kl.copy_dives([self.fin], ['1'], None, fl)
        kl.copy_dives([self.fin], ['1'], None, fl) # try to duplicate
        nodes = ku.find(fl, '//uddf:dive')

        dn = next(nodes)
        self.assertTrue(next(nodes, None) is None)


    @unittest.skip
    def test_dive_copy_with_site(self):
        """
        Test copying dive with dive site
        """
        fl = '{}/dive_copy_logbook.uddf'.format(self.tdir)
        kl.copy_dive(self.fin, 1, fl)
        nodes = ku.find(fl, '//uddf:dive')

        dn = next(nodes)
        self.assertEquals('2009-09-19T13:10:23',
                ku.xp_first(dn, './/uddf:datetime/text()'))
        self.assertEquals('konig', ku.xp_first(dn, './/uddf:link/@ref'))


    @unittest.skip
    def test_dive_copy_with_buddy(self):
        """
        Test copying a dive with a buddy
        """
        fl = '{}/dive_copy_logbook.uddf'.format(self.tdir)
        kl.copy_dive(self.fin, 1, fl)
        nodes = ku.find(fl, '//uddf:dive')

        dn = next(nodes)
        self.assertEquals('2009-09-19T13:10:23',
                ku.xp_first(dn, './/uddf:datetime/text()'))
        self.assertEquals('b1', ku.xp_first(dn, './/uddf:link/@ref'))


    @unittest.skip
    def test_dive_copy_with_buddies(self):
        """
        Test dive copying with dive buddies
        """
        fl = '{}/dive_copy_logbook.uddf'.format(self.tdir)
        kl.copy_dive(self.fin, 2, fl)
        nodes = ku.find(fl, '//uddf:dive')

        dn = next(nodes)
        self.assertEquals('2010-10-30T13:24:43',
                ku.xp_first(dn, './/uddf:datetime/text()'))
        self.assertEquals(('b1', 'b2'), tuple(ku.xp(dn, './/uddf:link/@ref')))


    def test_dive_copy_with_gases(self):
        """
        Test dive copying with gas data
        """
        fl = '{}/dive_copy_logbook.uddf'.format(self.tdir)

        kl.copy_dives([self.fin], ['1'], None, fl)
        nodes = ku.find(fl, '//uddf:dive')

        dn = next(nodes)
        self.assertEquals(('air', 'ean39'),
                tuple(ku.xp(dn, './/uddf:switchmix/@ref')))


    def test_dive_copy_with_no_gases(self):
        """
        Test copying dives having no gas data
        """
        fl = '{}/dive_copy_logbook.uddf'.format(self.tdir)

        kl.copy_dives([self.fin], ['2'], None, fl)
        nodes = ku.find(fl, '//uddf:dive')

        dn = next(nodes)
        self.assertEquals([], list(ku.xp(dn, './/uddf:switchmix/@ref')))


    def test_dive_copy_gases_retain(self):
        """
        Test copying dives with no gas data to existing logbook
        """
        fl = '{}/dive_copy_logbook.uddf'.format(self.tdir)

        kl.copy_dives([self.fin], ['1'], None, fl) # copy gases in
        kl.copy_dives([self.fin], ['2'], None, fl) # copy no gases

        nodes = ku.find(fl, '//uddf:dive')
        dn = next(nodes) # 1st dive shall have gases
        self.assertEquals(('air', 'ean39'),
                tuple(ku.xp(dn, './/uddf:switchmix/@ref')))

        # gas definition section shall be intact
        nodes = ku.find(fl, '//uddf:gasdefinitions')
        self.assertTrue(next(nodes) is not None)



class DiveFindingTestCase(unittest.TestCase):
    """
    Tests for finding dive data in files.
    """
    def setUp(self):
        """
        Create testing documents.
        """
        from kenozooid.tests.test_uddf import UDDF_PROFILE
        self.f1 = BytesIO(UDDF_PROFILE)
        self.f2 = BytesIO(UDDF_PROFILE)
        self.f3 = BytesIO(UDDF_PROFILE)


    def test_all_nodes_find(self):
        """
        Test finding all dive nodes from UDDF files
        """
        nodes = list(kl.find_dive_nodes([self.f1, self.f2, self.f3],
            ['1-2', None, '3']))
        self.assertEquals(6, len(nodes))


    def test_find_with_incomplete(self):
        """
        Test finding dive nodes from UDDF files with incomplete collection of numeric ranges
        """
        nodes = list(kl.find_dive_nodes([self.f1, self.f2, self.f3], ['1-2']))
        self.assertEquals(8, len(nodes))


    def test_find_with_dive_number(self):
        """
        Test finding dive nodes from UDDF files with dive number
        """
        nodes = list(kl.find_dive_nodes([self.f1, self.f2, self.f3], None,
            '299-302'))
        self.assertEquals(3, len(nodes))

        ids = [ku.xp_first(n, '@id') for n in nodes]
        self.assertEquals(['d01'] * 3, ids)



class DiveEnumIntegrationTestCase(IntegrationTestCaseBase):
    """
    Dive enumeration integration tests.
    """
    def setUp(self):
        """
        Prepare input file.
        """
        super().setUp()
        fin = self.fin = '{}/dive_enum_in.uddf'.format(self.tdir)
        f = open(fin, 'wb')
        f.write(ktu.UDDF_PROFILE)
        f.close()


    def test_dive_enum(self):
        """
        Test enumerating dives
        """
        kl.enum_dives([self.fin])
        r = ku.find(self.fin, '//uddf:dive//uddf:divenumber/text()')
        self.assertEquals(['1', '2', '3'], list(r))


    def test_dive_reenum(self):
        """
        Test re-enumerating dives
        """
        kl.enum_dives([self.fin])

        r = ku.find(self.fin, '//uddf:dive//uddf:divenumber/text()')
        assert ['1', '2', '3'] == list(r)

        d = kd.Dive(datetime=datetime(2010, 1, 2, 5, 7), depth=33.0,
                duration=3540)
        kl.add_dive(d, self.fin)
        kl.enum_dives([self.fin]) # re-enumerate
        r = ku.find(self.fin, '//uddf:dive//uddf:divenumber/text()')
        self.assertEquals(['1', '2', '3', '4'], list(r))


# vim: sw=4:et:ai
