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

class DiveAddingIntegrationTestCase(unittest.TestCase):
    """
    Dive adding integration tests.
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


    def test_dive_add(self):
        """
        Test adding dive with time, depth and duration
        """
        f = '{}/dive_add.uddf'.format(self.tdir)
        kl.add_dive(f, datetime(2010, 1, 2, 5, 7), 33.0, 59)
        nodes = ku.parse(f, '//uddf:dive')

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

        kl.add_dive(f, datetime(2010, 1, 2, 5, 7), 33.0, 59, qsite='s1')

        nodes = ku.parse(f, '//uddf:dive')
        dn = next(nodes)
        self.assertTrue('s1', ku.xp_first(dn, './/uddf:link/@ref'))


    def test_dive_add_with_buddy(self):
        """
        Test adding dive with time, depth, duration and buddy
        """
        f = '{}/dive_add_buddy.uddf'.format(self.tdir)

        doc = ku.create()
        ku.create_buddy_data(doc, id='b1', fname='F', lname='N');
        ku.save(doc, f)

        kl.add_dive(f, datetime(2010, 1, 2, 5, 7), 33.0, 59,
                qbuddies=['b1'])

        nodes = ku.parse(f, '//uddf:dive')
        dn = next(nodes)
        self.assertTrue('b1', ku.xp_first(dn, './/uddf:link/@ref'))


    def test_dive_add_with_buddies(self):
        """
        Test adding dive with time, depth, duration and two buddies
        """
        f = '{}/dive_add_buddy.uddf'.format(self.tdir)

        doc = ku.create()
        ku.create_buddy_data(doc, id='b1', fname='F', lname='N');
        ku.create_buddy_data(doc, id='b2', fname='F', lname='N');
        ku.save(doc, f)

        kl.add_dive(f, datetime(2010, 1, 2, 5, 7), 33.0, 59,
                qbuddies=['b1'])

        nodes = ku.parse(f, '//uddf:dive')
        dn = next(nodes)
        self.assertTrue(('b1', 'b2'), tuple(ku.xp(dn, './/uddf:link/@ref')))


    def test_dive_with_profile(self):
        """
        Test adding dive with dive profile.
        """
        import kenozooid.tests.test_uddf as ktu
        pf = '{}/dive_add_profile.uddf'.format(self.tdir)
        f = open(pf, 'wb')
        f.write(ktu.UDDF_PROFILE)
        f.close()

        f = '{}/dive_add.uddf'.format(self.tdir)
        kl.add_dive(f, dive_no=1, pfile=pf)
        nodes = ku.parse(f, '//uddf:dive')

        dn = next(nodes)
        self.assertTrue(next(nodes, None) is None)

        self.assertEquals('2009-09-19T13:10:23',
            ku.xp_first(dn, './/uddf:datetime/text()'))
        self.assertEquals('30.2',
            ku.xp_first(dn, './/uddf:greatestdepth/text()'))
        self.assertEquals('20',
            ku.xp_first(dn, './/uddf:diveduration/text()'))


    def test_dive_with_profile_with_site(self):
        """
        Test adding dive with dive profile and dive site
        """
        import kenozooid.tests.test_uddf as ktu
        pf = '{}/dive_add_profile.uddf'.format(self.tdir)
        f = open(pf, 'wb')
        f.write(ktu.UDDF_PROFILE)
        f.close()

        f = '{}/dive_add.uddf'.format(self.tdir)

        doc = ku.create()
        ku.create_site_data(doc, id='s1', location='L1', name='N1')
        ku.save(doc, f)

        kl.add_dive(f, dive_no=1, pfile=pf)
        nodes = ku.parse(f, '//uddf:dive')

        dn = next(nodes)
        self.assertTrue('s1', ku.xp_first(dn, './/uddf:link/@ref'))


    def test_dive_with_profile_with_buddy(self):
        """
        Test adding dive with dive profile and a buddy
        """
        import kenozooid.tests.test_uddf as ktu
        pf = '{}/dive_add_profile.uddf'.format(self.tdir)
        f = open(pf, 'wb')
        f.write(ktu.UDDF_PROFILE)
        f.close()

        f = '{}/dive_add.uddf'.format(self.tdir)

        doc = ku.create()
        ku.create_buddy_data(doc, id='b1', fname='F', lname='N');
        ku.save(doc, f)

        kl.add_dive(f, dive_no=1, pfile=pf)
        nodes = ku.parse(f, '//uddf:dive')

        dn = next(nodes)
        self.assertTrue('b1', ku.xp_first(dn, './/uddf:link/@ref'))


    def test_dive_with_profile_with_buddies(self):
        """
        Test adding dive with dive profile and dive buddies
        """
        import kenozooid.tests.test_uddf as ktu
        pf = '{}/dive_add_profile.uddf'.format(self.tdir)
        f = open(pf, 'wb')
        f.write(ktu.UDDF_PROFILE)
        f.close()

        f = '{}/dive_add.uddf'.format(self.tdir)

        doc = ku.create()
        ku.create_buddy_data(doc, id='b1', fname='F1', lname='N1');
        ku.create_buddy_data(doc, id='b2', fname='F2', lname='N2');
        ku.save(doc, f)

        kl.add_dive(f, dive_no=1, pfile=pf)
        nodes = ku.parse(f, '//uddf:dive')

        dn = next(nodes)
        self.assertTrue(('b1', 'b2'), tuple(ku.xp(dn, './/uddf:link/@ref')))



# vim: sw=4:et:ai
