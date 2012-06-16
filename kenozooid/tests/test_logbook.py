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
import unittest

import kenozooid.logbook as kl
import kenozooid.uddf as ku

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
        kl.add_dive(datetime(2010, 1, 2, 5, 7), 33.0, 59, f)
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

        kl.add_dive(datetime(2010, 1, 2, 5, 7), 33.0, 59, f, qsite='s1')

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

        kl.add_dive(datetime(2010, 1, 2, 5, 7), 33.0, 59, f,
                qbuddies=['b1'])

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

        kl.add_dive(datetime(2010, 1, 2, 5, 7), 33.0, 59, f,
                qbuddies=['b1', 'b2'])

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
        import kenozooid.tests.test_uddf as ktu
        fin = self.fin = '{}/dive_copy_in.uddf'.format(self.tdir)
        f = open(fin, 'wb')
        f.write(ktu.UDDF_PROFILE)
        f.close()


    def test_dive_copy(self):
        """
        Test copying dive
        """
        fl = '{}/dive_copy_logbook.uddf'.format(self.tdir)
        kl.copy_dive(self.fin, 1, fl)
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
        kl.copy_dive(self.fin, 1, fl)
        kl.copy_dive(self.fin, 1, fl) # try to duplicate
        nodes = ku.find(fl, '//uddf:dive')

        dn = next(nodes)
        self.assertTrue(next(nodes, None) is None)


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

        kl.copy_dive(self.fin, 1, fl)
        nodes = ku.find(fl, '//uddf:dive')

        dn = next(nodes)
        self.assertEquals(('air', 'ean39'),
                tuple(ku.xp(dn, './/uddf:switchmix/@ref')))



class GasesCopyingIntegrationTestCase(IntegrationTestCaseBase):
    """
    Gases copying tests.
    """
    def test_copying_gases(self):
        """
        """
        import kenozooid.tests.test_uddf as ktu
        fin = '{}/dive_copy_in.uddf'.format(self.tdir)
        f = open(fin, 'wb')
        f.write(ktu.UDDF_PROFILE)
        f.close()

        fl = '{}/dive_copy_logbook.uddf'.format(self.tdir)
        doc = ku.create()
        kl.copy_gases(fin, 1, doc)
        ku.save(doc, fl)

        self.assertEquals(('air', 'ean39'), tuple(ku.find(fl,
            '//uddf:mix/@id')))


# vim: sw=4:et:ai
