#
# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2013 by Artur Wroblewski <wrobell@pld-linux.org>
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

from collections import namedtuple

from kenozooid.plan.deco import plan_deco_dive, deco_stops, dive_slate, \
    DiveProfile, DiveProfileType, GasList, parse_gas, parse_gas_list
from kenozooid.data import gas

import unittest
from unittest import mock


class DecoDivePlannerTestCase(unittest.TestCase):
    """
    Decompression dive planner tests.
    """
    def test_deco_dive_plan(self):
        """
        Test deco dive plan
        """
        ean50 = gas(50, 0, 22)
        ean80 = gas(80, 0, 9)
        air = gas(21, 0, depth=0)
        gas_list = GasList(air)
        gas_list.deco_gas.append(ean50)
        gas_list.deco_gas.append(ean80)

        plan = plan_deco_dive(gas_list, 45, 35)

        self.assertEquals(4, len(plan.profiles))

        t = DiveProfileType
        expected = [t.PLANNED, t.EXTENDED, t.LOST_GAS, t.EXTENDED_LOST_GAS]
        types = [p.type for p in plan.profiles]
        self.assertEquals(expected, types)

        self.assertEquals(45, plan.profiles[0].depth)
        self.assertEquals(35, plan.profiles[0].time)
        self.assertEquals(50, plan.profiles[1].depth)
        self.assertEquals(38, plan.profiles[1].time)
        self.assertEquals(45, plan.profiles[2].depth)
        self.assertEquals(35, plan.profiles[2].time)
        self.assertEquals(50, plan.profiles[3].depth)
        self.assertEquals(38, plan.profiles[3].time)

        # check deco gas
        self.assertEquals([ean50, ean80], plan.profiles[0].gas_list.deco_gas)
        self.assertEquals([ean50, ean80], plan.profiles[1].gas_list.deco_gas)
        self.assertEquals([], plan.profiles[2].gas_list.deco_gas)
        self.assertEquals([], plan.profiles[3].gas_list.deco_gas)

        # check bottom gas
        self.assertEquals(air, plan.profiles[0].gas_list.bottom_gas)
        self.assertEquals(air, plan.profiles[1].gas_list.bottom_gas)
        self.assertEquals(air, plan.profiles[2].gas_list.bottom_gas)
        self.assertEquals(air, plan.profiles[3].gas_list.bottom_gas)


    @mock.patch('decotengu.create')
    def test_deco_stops(self, f_c):
        """
        Test deco dive plan deco stops calculator

        Verify that

        - gas mixes are passed correctly to the deco engine
        - decompression stops are returned
        """
        engine = mock.MagicMock()
        dt = mock.MagicMock()
        f_c.return_value = engine, dt

        gas_list = GasList(gas(27, 0, depth=33))
        gas_list.travel_gas.append(gas(32, 0, depth=0))
        gas_list.deco_gas.append(gas(50, 0, depth=22))
        gas_list.deco_gas.append(gas(80, 0, depth=10))

        p = DiveProfile(DiveProfileType.PLANNED, gas_list, 45, 35)
        stops = deco_stops(p)

        args = engine.add_gas.call_args_list
        print(dir(args[0]))
        # check travel gas
        self.assertEquals(((0, 32, 0), {'travel': True}), args[0])
        # check bottom gas
        self.assertEquals(((33, 27, 0),), args[1])
        # check deco gas
        self.assertEquals(((22, 50, 0),), args[2])
        self.assertEquals(((10, 80, 0),), args[3])

        # check deco stops are returned
        self.assertEquals(dt.stops, stops)


    def test_dive_slate(self):
        """
        Test dive slate creation
        """
        ean27 = gas(27, 0, depth=33)
        ean50 = gas(50, 0, depth=22)
        ean80 = gas(80, 0, depth=10)

        gas_list = GasList(ean27)
        gas_list.deco_gas.append(ean50)
        gas_list.deco_gas.append(ean80)

        profile = DiveProfile(DiveProfileType.PLANNED, gas_list, 45, 35)

        Stop = namedtuple('Stop', 'depth time')
        stops = [
            Stop(18, 1),
            Stop(15, 1),
            Stop(12, 2),
            Stop(9, 3),
            Stop(6, 5),
        ]

        slate = dive_slate(profile, stops)

        self.assertEquals(8, len(slate), slate)

        self.assertEquals((45, None, 35, ean27), slate[0], slate)
        self.assertEquals((22, None, 37, ean50), slate[1], slate)
        # runtime = 38.7
        self.assertEquals((18, 1, 39, None), slate[2], slate)
        # runtime = 38.7 + 1.3
        self.assertEquals((15, 1, 40, None), slate[3], slate)
        # runtime = 40 + 2.3
        self.assertEquals((12, 2, 42, None), slate[4], slate)
        # runtime = 42.3 + 3.3
        self.assertEquals((9, 3, 46, ean80), slate[5], slate)
        # runtime = 45.6 + 5.3
        self.assertEquals((6, 5, 51, None), slate[6], slate)
        # runtime = 50.9 + 0.6 = 51.4999...
        self.assertEquals((0, None, 51, None), slate[7], slate)


    def test_dive_slate_travel(self):
        """
        Test dive slate creation (with travel gas)
        """
        ean32 = gas(32, 0, depth=0)
        ean30 = gas(30, 0, depth=33)
        ean27 = gas(27, 0, depth=37)
        ean50 = gas(50, 0, depth=22)
        ean80 = gas(80, 0, depth=10)

        gas_list = GasList(ean27)
        gas_list.travel_gas.append(ean32)
        gas_list.travel_gas.append(ean30)
        gas_list.deco_gas.append(ean50)
        gas_list.deco_gas.append(ean80)

        profile = DiveProfile(DiveProfileType.PLANNED, gas_list, 45, 35)

        Stop = namedtuple('Stop', 'depth time')
        stops = [
            Stop(18, 1),
            Stop(15, 1),
            Stop(12, 2),
            Stop(9, 3),
            Stop(6, 5),
        ]

        slate = dive_slate(profile, stops)

        self.assertEquals((0, None, 0, ean32), slate[0], slate)
        self.assertEquals((33, None, 3, ean30), slate[1], slate)
        self.assertEquals((37, None, 4, ean27), slate[2], slate)
        self.assertEquals((45, None, 35, None), slate[3], slate)


class GasMixParserTestCase(unittest.TestCase):
    """
    Gas mix parser tests.
    """
    def test_parse_gas_air(self):
        """
        Test parsing air gas mix
        """
        m = parse_gas('air')
        self.assertEquals(21, m.o2)
        self.assertEquals(0, m.he)
        self.assertEquals(66, m.depth)

        m = parse_gas('air@0')
        self.assertEquals(21, m.o2)
        self.assertEquals(0, m.he)
        self.assertEquals(0, m.depth)


    def test_parse_gas_o2(self):
        """
        Test parsing o2 gas mix
        """
        m = parse_gas('o2')
        self.assertEquals(100, m.o2)
        self.assertEquals(0, m.he)
        self.assertEquals(6, m.depth)


    def test_parse_gas_ean(self):
        """
        Test parsing EAN gas mix
        """
        m = parse_gas('EAN50')
        self.assertEquals(50, m.o2)
        self.assertEquals(0, m.he)
        self.assertEquals(22, m.depth)

        m = parse_gas('ean32@21')
        self.assertEquals(32, m.o2)
        self.assertEquals(0, m.he)
        self.assertEquals(21, m.depth)


    def test_parse_trimix(self):
        """
        Test parsing trimix gas
        """
        m = parse_gas('TX21/33@10')
        self.assertEquals(21, m.o2)
        self.assertEquals(33, m.he)
        self.assertEquals(10, m.depth)

        m = parse_gas('TX17/18')
        self.assertEquals(17, m.o2)
        self.assertEquals(18, m.he)
        self.assertEquals(84, m.depth)

    # TODO: 'TX17/18|2x12', 'TX21/33@10'

    def test_parse_gas_unknown(self):
        """
        Test parsing unknown gas mix
        """
        mixes = [
            'EAN50/30', 'O2/30', 'EAN', 'TX@20', 'TX/30', 'EAN100',
            'TX100/10'
        ]
        for m in mixes:
            self.assertTrue(parse_gas(m) is None, m)


    def test_parse_gas_list(self):
        """
        Test parsing gas list
        """
        air = gas(21, 0)
        ean50 = gas(50, 0, 22)
        gas_list = parse_gas_list('air@0', 'ean50')
        self.assertEquals([], gas_list.travel_gas)
        self.assertEquals(air, gas_list.bottom_gas)
        self.assertEquals([ean50], gas_list.deco_gas)


# vim: sw=4:et:ai
