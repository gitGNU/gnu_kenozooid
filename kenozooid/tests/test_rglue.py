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
rpy integration functions tests.
"""

from datetime import datetime
import unittest

import rpy2.robjects as ro
R = ro.r

from kenozooid.rglue import _vec, bool_vec, float_vec, str_vec, int_vec, df, \
    dives_df, dive_profiles_df, inject_dive_data
import kenozooid.data as kd

class FloatVectorTestCase(unittest.TestCase):
    """
    Float vector tests.
    """
    def test_vec(self):
        """
        Test creation of float vector
        """
        t = (1.0, 2.0, 3.0)
        v = float_vec(t)
        self.assertEquals(t, tuple(v))


    def test_na_vec(self):
        """
        Test creation of float vector with None values
        """
        t = (1.0, 2.0, None, 4.0)
        v = float_vec(t)
        e = (1.0, 2.0, ro.NA_Real, 4.0)
        self.assertEquals(e, tuple(v))



class BoolVectorTestCase(unittest.TestCase):
    """
    Bool vector tests.
    """
    def test_vec(self):
        """
        Test creation of bool vector
        """
        t = (True, True, False)
        v = bool_vec(t)
        self.assertEquals(t, tuple(v))


    def test_na_vec(self):
        """
        Test creation of bool vector with None values
        """
        t = (False, True, None, False)
        v = bool_vec(t)
        self.assertEquals((False, True, ro.NA_Logical, False), tuple(v))


class DataFrameTestCase(unittest.TestCase):
    """
    Data frame creation tests.
    """
    def test_df(self):
        """
        Test basic data frame creation
        """
        r1 = (1, True)
        r2 = (2, False)
        r3 = (4, None)
        d = df(('a', 'b'), (float_vec, bool_vec), iter((r1, r2, r3)))
        # check columns
        self.assertEquals((1.0, 2.0, 4.0), tuple(d[0]))
        self.assertEquals((True, False, ro.NA_Logical), tuple(d[1]))



class DiveDataInjectTestCase(unittest.TestCase):
    """
    Dive data inject tests.
    """
    def test_dives_df(self):
        """
        Test dive data frame creation
        """
        dives = (
            (datetime(2011, 10, 11), 31.0, 2010, 12),
            (datetime(2011, 10, 12), 32.0, 2020, 14),
            (datetime(2011, 10, 13), 33.0, 2030, None),
        )
        d = dives_df(dives)
        self.assertEquals(3, d.nrow)
        self.assertEquals(4, d.ncol)
        #self.assertEquals((), tuple(d[0]))
        self.assertEquals((31.0, 32.0, 33.0), tuple(d[1]))
        self.assertEquals((2010, 2020, 2030), tuple(d[2]))
        self.assertEquals((12, 14, ro.NA_Real), tuple(d[3]))


    def test_dive_profiles_df(self):
        """
        Test dive profiles data frame creation
        """
        p1 = (
            kd.Sample(time=0, depth=10.0, temp=15.0, alarm=False),
            kd.Sample(time=10, depth=20.0, temp=14.0, alarm=False),
            kd.Sample(time=20, depth=10.0, temp=13.0, alarm=False),
        )
        p2 = (
            kd.Sample(time=1, depth=10.0, temp=15.0, alarm=False),
            kd.Sample(time=11, depth=20.0, temp=14.0, deco_time=4, deco_depth=9, alarm=False),
            kd.Sample(time=21, depth=10.0, temp=13.0, alarm=False),
        )
        p3 = (
            kd.Sample(time=2, depth=10.0, temp=15.0, alarm=False),
            kd.Sample(time=12, depth=20.0, temp=14.0, deco_time=1, deco_depth=6, alarm=True),
            kd.Sample(time=22, depth=12.0, temp=11.0, alarm=False),
            kd.Sample(time=23, depth=11.0, temp=12.0, alarm=False),
            kd.Sample(time=25, depth=10.0, temp=11.0, alarm=False),
        )
        d = dive_profiles_df((p1, p2, p3))
        self.assertEquals(11, d.nrow)
        self.assertEquals(13, d.ncol)
        self.assertEquals((1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3), tuple(d[0]))
        self.assertEquals((10.0, 20.0, 10.0, 10.0, 20.0, 10.0, 10.0, 20.0,
            12.0, 11.0, 10.0), tuple(d[1]))
        self.assertEquals((0, 10, 20, 1, 11, 21, 2, 12, 22, 23, 25), tuple(d[2]))


    def test_dive_data_injection(self):
        """
        Test dive data injection
        """
        d1, d2, d3 = (
            (datetime(2011, 10, 11), 31.0, 2010, 12),
            (datetime(2011, 10, 12), 32.0, 2020, 14),
            (datetime(2011, 10, 13), 33.0, 2030, None),
        )
        p1 = (
            kd.Sample(time=0, depth=10.0, temp=15.0, alarm=False),
            kd.Sample(time=10, depth=20.0, temp=14.0, alarm=False),
            kd.Sample(time=20, depth=10.0, temp=13.0, alarm=False),
        )
        p2 = (
            kd.Sample(time=1, depth=10.0, temp=15.0, alarm=False),
            kd.Sample(time=11, depth=20.0, temp=14.0, deco_time=4, deco_depth=9, alarm=False),
            kd.Sample(time=21, depth=10.0, temp=13.0, alarm=False),
        )
        p3 = (
            kd.Sample(time=2, depth=10.0, temp=15.0, alarm=False),
            kd.Sample(time=12, depth=20.0, temp=14.0, deco_time=1, deco_depth=6, alarm=True),
            kd.Sample(time=22, depth=12.0, temp=11.0, alarm=False),
            kd.Sample(time=23, depth=11.0, temp=12.0, alarm=False),
            kd.Sample(time=25, depth=10.0, temp=11.0, alarm=False),
        )

        inject_dive_data(zip((d1, d2, d3), (p1, p2, p3)))

        d_df = ro.globalenv['kz.dives']

        self.assertEquals(3, d_df.nrow)
        self.assertEquals(4, d_df.ncol)
        self.assertEquals((31.0, 32.0, 33.0), tuple(d_df[1]))
        self.assertEquals((2010, 2020, 2030), tuple(d_df[2]))
        self.assertEquals((12, 14, ro.NA_Real), tuple(d_df[3]))

        p_df = ro.globalenv['kz.profiles']

        self.assertEquals(11, p_df.nrow)
        self.assertEquals(13, p_df.ncol)
        self.assertEquals((1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3), tuple(p_df[0]))
        self.assertEquals((10.0, 20.0, 10.0, 10.0, 20.0, 10.0, 10.0, 20.0,
            12.0, 11.0, 10.0), tuple(p_df[1]))
        self.assertEquals((0, 10, 20, 1, 11, 21, 2, 12, 22, 23, 25),
                tuple(p_df[2]))


# vim: sw=4:et:ai
