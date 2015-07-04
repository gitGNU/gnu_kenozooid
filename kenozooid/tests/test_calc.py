#
# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2014 by Artur Wroblewski <wrobell@pld-linux.org>
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
Tests for calculation methods.
"""

import unittest

from kenozooid.calc import ppg, pp_o2, pp_n2, mod, ead, rmv


class PPTestCase(unittest.TestCase):
    """
    Partial pressure tests.
    """
    def test_pp_o2(self):
        """
        Test air pp_o2 calculation
        """
        pp = pp_o2(57, 21)
        self.assertAlmostEqual(1.4, round(pp, 1), places=1)


    def test_pp_n2(self):
        """
        Test air pp_n2 calculation
        """
        pp = pp_n2(57, 21)
        self.assertAlmostEqual(6.7 - 1.4, round(pp, 1), places=1)


    def test_pp_o2_ean34(self):
        """
        Test EAN 34 pp_o2 calculation
        """
        pp = pp_o2(28, 34)
        self.assertAlmostEqual(1.292, pp, places=3)


    def test_pp_n2_ean34(self):
        """
        Test EAN 34 pp_n2 calculation
        """
        pp = pp_n2(28, 34)
        self.assertAlmostEqual(3.8 - 1.292, pp, places=3)



class MODTestCase(unittest.TestCase):
    """
    Maximum operating depth calculation tests.
    """
    def test_air(self):
        """
        Test MOD for air
        """
        d = mod(21)
        self.assertAlmostEqual(56.7, d, places=1)


    def test_EAN50(self):
        """Test EAN 50 MOD calculation at 1.6 pp_o2
        """
        d = mod(50, 1.6)
        self.assertAlmostEqual(22, d, places=1)


    def test_EAN80(self):
        """Test EAN 80 MOD calculation at 1.6 pp_o2
        """
        d = mod(80, 1.6)
        self.assertAlmostEqual(10, d, places=1)



class EADTestCase(unittest.TestCase):
    """
    Equivalent air depth calculation tests.
    """
    def test_EAN35(self):
        """Test EAN 35 EAD calculation
        """
        d = ead(30, 35)
        self.assertAlmostEqual(22.9, round(d, 1), places=1)



class RMVTestCase(unittest.TestCase):
    """
    Respiratory minute volume calculation tests.
    """
    def test_12_150_25_40(self):
        """
        Test 12l, 150bar, 25m, 40min RMV
        """
        v = rmv(12, 150, 25, 40)
        self.assertAlmostEqual(12.9, v, places=1)


    def test_15_160_20_42(self):
        """
        Test 12l, 160bar, 20m, 42min RMV
        """
        v = rmv(15, 160, 20, 42)
        self.assertAlmostEqual(19.0, v, places=1)


# vim: sw=4:et:ai
