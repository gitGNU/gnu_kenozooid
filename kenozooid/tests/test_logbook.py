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
Logbook tests.
"""

import shutil
import tempfile
from datetime import datetime
import unittest

import kenozooid.logbook as kl
import kenozooid.uddf as ku

class DiveAddingTestCase(unittest.TestCase):
    """
    Dive adding tests.
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


    def test_dive_with_profile(self):
        """
        Test adding dive with dive profile.
        """
        assert False


    def test_dive_add_with_site(self):
        """
        Test adding dive with time, depth, duration and dive site
        """
        assert False


    def test_dive_with_profile_with_site(self):
        """
        Test adding dive with dive profile and dive site
        """
        assert False


# vim: sw=4:et:ai
