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

from pprint import pformat
from collections import namedtuple, OrderedDict

from kenozooid.plan.deco import plan_deco_dive, deco_stops, dive_slate, \
    dive_legs, depth_to_time, gas_volume, parse_gas, parse_gas_list, \
    dive_legs_overhead, min_gas_volume, gas_vol_info, gas_mix_depth_update, \
    sum_deco_time, sum_dive_time, DivePlan, DiveProfile, ProfileType, GasList
from kenozooid.data import gas

import unittest
from unittest import mock

Stop = namedtuple('Stop', 'depth time')

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

        plan = DivePlan()
        plan_deco_dive(plan, gas_list, 45, 35)

        self.assertEqual(4, len(plan.profiles))

        t = ProfileType
        expected = [t.PLANNED, t.EXTENDED, t.LOST_GAS, t.EXTENDED_LOST_GAS]
        types = [p.type for p in plan.profiles]
        self.assertEqual(expected, types)

        self.assertEqual(45, plan.profiles[0].depth)
        self.assertEqual(35, plan.profiles[0].time)
        self.assertEqual(50, plan.profiles[1].depth)
        self.assertEqual(38, plan.profiles[1].time)
        self.assertEqual(45, plan.profiles[2].depth)
        self.assertEqual(35, plan.profiles[2].time)
        self.assertEqual(50, plan.profiles[3].depth)
        self.assertEqual(38, plan.profiles[3].time)

        # check deco gas
        self.assertEqual([ean50, ean80], plan.profiles[0].gas_list.deco_gas)
        self.assertEqual([ean50, ean80], plan.profiles[1].gas_list.deco_gas)
        self.assertEqual([], plan.profiles[2].gas_list.deco_gas)
        self.assertEqual([], plan.profiles[3].gas_list.deco_gas)

        # check bottom gas
        self.assertEqual(air, plan.profiles[0].gas_list.bottom_gas)
        self.assertEqual(air, plan.profiles[1].gas_list.bottom_gas)
        self.assertEqual(air, plan.profiles[2].gas_list.bottom_gas)
        self.assertEqual(air, plan.profiles[3].gas_list.bottom_gas)


    @mock.patch('decotengu.create')
    def test_deco_stops(self, f_c):
        """
        Test deco dive plan deco stops calculator

        Verify that

        - gas mixes are passed correctly to the deco engine
        - decompression stops are returned
        - default parameters are passed correctly to deco engine

        The test is DecoTengu library specific.
        """
        engine = mock.MagicMock()
        f_c.return_value = engine

        gas_list = GasList(gas(27, 0, depth=33))
        gas_list.travel_gas.append(gas(32, 0, depth=0))
        gas_list.deco_gas.append(gas(50, 0, depth=22))
        gas_list.deco_gas.append(gas(80, 0, depth=10))

        plan = DivePlan()
        p = DiveProfile(ProfileType.PLANNED, gas_list, 45, 35)
        stops = deco_stops(plan, p)

        args = engine.add_gas.call_args_list
        print(dir(args[0]))
        # check travel gas
        self.assertEqual(((0, 32, 0), {'travel': True}), args[0])
        # check bottom gas
        self.assertEqual(((33, 27, 0),), args[1])
        # check deco gas
        self.assertEqual(((22, 50, 0),), args[2])
        self.assertEqual(((10, 80, 0),), args[3])

        # check deco stops are returned
        self.assertEqual(engine.deco_table, stops)

        self.assertFalse(engine.last_stop_6m)
        self.assertEqual(0.3, engine.model.gf_low)
        self.assertEqual(0.85, engine.model.gf_high)


    @mock.patch('decotengu.create')
    def test_deco_stops_param_change(self, f_c):
        """
        Test deco dive plan deco stops calculator default params change

        Verify that dive decompression parameters are passed correctly to
        the deco engine. This test is DecoTengu decompression library
        specific.
        """
        engine = mock.MagicMock()
        f_c.return_value = engine
        gas_list = GasList(gas(27, 0, depth=33))

        plan = DivePlan()
        plan.gf_low = 10
        plan.gf_high = 95
        plan.last_stop_6m = True

        p = DiveProfile(ProfileType.PLANNED, gas_list, 45, 35)
        deco_stops(plan, p)

        self.assertTrue(engine.last_stop_6m)
        self.assertEqual(0.1, engine.model.gf_low)
        self.assertEqual(0.95, engine.model.gf_high)


    def test_dive_slate(self):
        """
        Test dive slate creation
        """
        ean27 = gas(27, 0, depth=0)
        ean50 = gas(50, 0, depth=22)
        ean80 = gas(80, 0, depth=10)

        gas_list = GasList(ean27)
        gas_list.deco_gas.append(ean50)
        gas_list.deco_gas.append(ean80)

        depth = 45
        time = 35
        descent_rate = 20

        profile = DiveProfile(ProfileType.PLANNED, gas_list, depth, time)

        stops = [
            Stop(18, 1),
            Stop(15, 1),
            Stop(12, 2),
            Stop(9, 3),
            Stop(6, 5),
        ]

        legs = dive_legs(profile, stops, descent_rate)
        slate = dive_slate(profile, stops, legs, descent_rate)

        msg = '\n{}\n{}'.format(pformat(legs), pformat(slate))
        self.assertEqual(8, len(slate), msg)

        self.assertEqual((45, None, 35, ean27), slate[0], slate)
        self.assertEqual((22, None, 37, ean50), slate[1], slate)
        # runtime = 38.7
        self.assertEqual((18, 1, 39, None), slate[2], slate)
        # runtime = 38.7 + 1.3
        self.assertEqual((15, 1, 40, None), slate[3], slate)
        # runtime = 40 + 2.3
        self.assertEqual((12, 2, 42, None), slate[4], slate)
        # runtime = 42.3 + 3.3
        self.assertEqual((9, 3, 46, ean80), slate[5], slate)
        # runtime = 45.6 + 5.3
        self.assertEqual((6, 5, 51, None), slate[6], slate)
        # runtime = 50.9 + 0.6 = 51.4999...
        self.assertEqual((0, None, 51, None), slate[7], slate)


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

        depth = 45
        time = 35
        descent_rate = 20

        profile = DiveProfile(ProfileType.PLANNED, gas_list, depth, time)

        stops = [
            Stop(18, 1),
            Stop(15, 1),
            Stop(12, 2),
            Stop(9, 3),
            Stop(6, 5),
        ]

        legs = dive_legs(profile, stops, descent_rate)
        slate = dive_slate(profile, stops, legs, descent_rate)

        self.assertEqual((0, None, 0, ean32), slate[0], slate)
        self.assertEqual((33, None, 2, ean30), slate[1], slate)
        self.assertEqual((37, None, 2, ean27), slate[2], slate)
        self.assertEqual((45, None, 35, None), slate[3], slate)
        self.assertEqual((22, None, 38, ean50), slate[4], slate)
        self.assertEqual((18, 1, 39, None), slate[5], slate)
        self.assertEqual((9, 3, 46, ean80), slate[8], slate)


    def test_dive_slate_travel_no_deco(self):
        """
        Test dive slate creation (with travel gas, no deco gas)
        """
        ean32 = gas(32, 0, depth=0)
        ean30 = gas(30, 0, depth=33)
        ean27 = gas(27, 0, depth=37)

        gas_list = GasList(ean27)
        gas_list.travel_gas.append(ean32)
        gas_list.travel_gas.append(ean30)

        depth = 45
        time = 35
        descent_rate = 20

        profile = DiveProfile(ProfileType.PLANNED, gas_list, depth, time)

        stops = [
            Stop(18, 1),
            Stop(15, 1),
            Stop(12, 2),
            Stop(9, 3),
            Stop(6, 5),
        ]

        legs = dive_legs(profile, stops, descent_rate)
        slate = dive_slate(profile, stops, legs, descent_rate)

        self.assertEqual((0, None, 0, ean32), slate[0], slate)
        self.assertEqual((33, None, 2, ean30), slate[1], slate)
        self.assertEqual((37, None, 2, ean27), slate[2], slate)
        self.assertEqual((45, None, 35, None), slate[3], slate)
        self.assertEqual((18, 1, 39, None), slate[4], slate)
        self.assertEqual((9, 3, 46, None), slate[7], slate)


    def test_depth_to_time_ascent(self):
        """
        Test depth to time conversion (ascent)

        The time is expected to be > 0.
        """
        t = depth_to_time(45, 10, 10)
        self.assertEqual(3.5, t)


    def test_depth_to_time_descent(self):
        """
        Test depth to time conversion (descent)

        The time is expected to be > 0.
        """
        t = depth_to_time(0, 45, 20)
        self.assertEqual(2.25, t)


    def test_sum_deco_time(self):
        """
        Test calculating dive decompression time
        """
        legs = [
            (0, 10, 1, 'A', False),
            (10, 40, 3, 'B', False),
            (40, 40, 30, None, False),
            (40, 15, 2.5, None, False),
            (15, 15, 1, None, True),
            (15, 12, 0.3, None, True),
            (12, 12, 1, None, True),
            (12, 9, 0.3, None, True),
            (9, 9, 3, None, True),
            (9, 6, 0.3, None, True),
            (6, 6, 5, None, True),
            (6, 0, 0.6, None, True),
        ]
        t = sum_deco_time(legs)
        self.assertAlmostEquals(10 + 1.5, t)


    def test_sum_dive_time(self):
        """
        Test calculating total dive time
        """
        legs = [
            (0, 10, 1, 'A', False),
            (10, 40, 3, 'B', False),
            (40, 40, 30, None, False),
            (40, 15, 2.5, None, False),
            (15, 15, 1, None, True),
            (15, 12, 0.3, None, True),
            (12, 12, 1, None, True),
            (12, 9, 0.3, None, True),
            (9, 9, 3, None, True),
            (9, 6, 0.3, None, True),
            (6, 6, 5, None, True),
            (6, 0, 0.6, None, True),
        ]
        t = sum_dive_time(legs)
        self.assertAlmostEquals(4 + 30 + 2.5 + 10 + 1.5, t)



class GasMixDepthUpdateTestCase(unittest.TestCase):
    """
    Gas mix switch depth update tests.
    """
    def test_bottom_gas_mix_no_travel(self):
        """
        Test bottom gas mix depth update when no travel gas mix
        """
        air = gas(21, 0, None)

        gas_list = GasList(air)
        result = gas_mix_depth_update(gas_list, 1.4, 1.6)
        self.assertEqual(0, result.bottom_gas.depth)


    def test_bottom_gas_mix_with_travel(self):
        """
        Test bottom gas mix depth update when travel gas mix added
        """
        ean50 = gas(50, 0, None)
        air = gas(21, 0, None)

        gas_list = GasList(air)
        gas_list.travel_gas = [ean50]

        result = gas_mix_depth_update(gas_list, 1.4, 1.6)

        self.assertEqual(1, len(result.travel_gas))
        self.assertEqual(0, result.travel_gas[0].depth)
        self.assertEqual(18, result.bottom_gas.depth)


    def test_travel_gas_mix(self):
        """
        Test travel gas mix depth update
        """
        ean50 = gas(50, 0, None)
        ean32 = gas(32, 0, None)
        air = gas(21, 0, None)

        gas_list = GasList(air)
        gas_list.travel_gas = [ean50, ean32]

        result = gas_mix_depth_update(gas_list, 1.4, 1.6)

        self.assertEqual(2, len(result.travel_gas))
        self.assertEqual(0, result.travel_gas[0].depth)
        self.assertEqual(18, result.travel_gas[1].depth)
        self.assertEqual(33, result.bottom_gas.depth)


    def test_deco_gas_mix(self):
        """
        Test deco gas mix depth update
        """
        air = gas(21, 0, None)
        ean50 = gas(50, 0, None)
        o2 = gas(100, 0, 6)

        gas_list = GasList(air)
        gas_list.deco_gas = [ean50, o2]

        result = gas_mix_depth_update(gas_list, 1.4, 1.6)

        m1, m2 = result.deco_gas
        self.assertEqual(22, m1.depth)
        self.assertEqual(6, m2.depth)



class GasMixParserTestCase(unittest.TestCase):
    """
    Gas mix parser tests.
    """
    def test_parse_gas_air(self):
        """
        Test parsing air gas mix
        """
        m = parse_gas('air')
        self.assertEqual(21, m.o2)
        self.assertEqual(0, m.he)
        self.assertTrue(m.depth is None)

        m = parse_gas('air@0')
        self.assertEqual(21, m.o2)
        self.assertEqual(0, m.he)
        self.assertEqual(0, m.depth)


    def test_parse_gas_o2(self):
        """
        Test parsing o2 gas mix
        """
        m = parse_gas('o2@6')
        self.assertEqual(100, m.o2)
        self.assertEqual(0, m.he)
        self.assertEqual(6, m.depth)


    def test_parse_gas_ean(self):
        """
        Test parsing EAN gas mix
        """
        m = parse_gas('EAN50')
        self.assertEqual(50, m.o2)
        self.assertEqual(0, m.he)
        self.assertTrue(m.depth is None)

        m = parse_gas('ean32@21')
        self.assertEqual(32, m.o2)
        self.assertEqual(0, m.he)
        self.assertEqual(21, m.depth)


    def test_parse_trimix(self):
        """
        Test parsing trimix gas
        """
        m = parse_gas('TX21/33@10')
        self.assertEqual(21, m.o2)
        self.assertEqual(33, m.he)
        self.assertEqual(10, m.depth)

        m = parse_gas('TX17/18')
        self.assertEqual(17, m.o2)
        self.assertEqual(18, m.he)
        self.assertTrue(m.depth is None)

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
        ean50 = gas(50, 0, None)
        gas_list = parse_gas_list('air@0', 'ean50')
        self.assertEqual([], gas_list.travel_gas)
        self.assertEqual(air, gas_list.bottom_gas)
        self.assertEqual([ean50], gas_list.deco_gas)



class DiveLegsTestCase(unittest.TestCase):
    """
    Dive legs calculation tests.
    """
    def test_dive_legs(self):
        """
        Test dive legs calculation
        """
        air = gas(21, 0)
        gas_list = GasList(air)
        stops = [
            Stop(18, 1),
            Stop(15, 1),
            Stop(12, 2),
            Stop(9, 3),
            Stop(6, 5),
        ]
        profile = DiveProfile(ProfileType.PLANNED, gas_list, 60, 25)

        legs = dive_legs(profile, stops, 20)

        self.assertEqual(3 + 10, len(legs))
        self.assertEqual((0, 60, 3, air, False), legs[0])
        self.assertEqual((60, 60, 22, air, False), legs[1])
        self.assertEqual((60, 18, 4.2, air, False), legs[2])

        deco_legs = legs[3::2]
        for s, l in zip(stops, deco_legs):
            self.assertEqual((s.depth, s.depth, s.time, air, True), l)

        self.assertEqual((6, 0, 0.6, air, True), legs[-1])


    def test_dive_legs_deco_gas(self):
        """
        Test dive legs calculation with deco gas
        """
        air = gas(21, 0)
        ean50 = gas(50, 0, 22)
        ean80 = gas(80, 0, 10)
        o2 = gas(100, 0, 6)
        gas_list = GasList(air)
        gas_list.deco_gas.extend((ean50, ean80, o2))
        stops = [
            Stop(18, 1),
            Stop(15, 1),
            Stop(12, 2),
            Stop(9, 3),
            Stop(6, 5),
        ]
        profile = DiveProfile(ProfileType.PLANNED, gas_list, 60, 25)

        legs = dive_legs(profile, stops, 20)

        self.assertEqual(4 + 10, len(legs))
        self.assertEqual((0, 60, 3, air, False), legs[0])
        self.assertEqual((60, 60, 22, air, False), legs[1])
        self.assertEqual((60, 22, 3.8, air, False), legs[2])
        self.assertEqual((22, 18, 0.4, ean50, False), legs[3])

        self.assertEqual((18, 18, 1, ean50, True), legs[4])
        self.assertEqual((18, 15, 0.3, ean50, True), legs[5])
        self.assertEqual((15, 15, 1, ean50, True), legs[6])
        self.assertEqual((15, 12, 0.3, ean50, True), legs[7])

        self.assertEqual((12, 12, 2, ean50, True), legs[8])
        self.assertEqual((12, 9, 0.3, ean50, True), legs[9])
        self.assertEqual((9, 9, 3, ean80, True), legs[10])
        self.assertEqual((9, 6, 0.3, ean80, True), legs[11])

        self.assertEqual((6, 6, 5, o2, True), legs[-2])
        self.assertEqual((6, 0, 0.6, o2, True), legs[-1])


    def test_dive_legs_travel_gas(self):
        """
        Test dive legs calculation with travel gas
        """
        ean36 = gas(36, 0, depth=0)
        ean26 = gas(26, 0, depth=30)
        air = gas(21, 0, depth=40)
        gas_list = GasList(air)
        gas_list.travel_gas.append(ean36)
        gas_list.travel_gas.append(ean26)
        stops = [
            Stop(18, 1),
            Stop(15, 1),
            Stop(12, 2),
            Stop(9, 3),
            Stop(6, 5),
        ]

        profile = DiveProfile(ProfileType.PLANNED, gas_list, 60, 25)
        legs = dive_legs(profile, stops, 20)

        self.assertEqual(5 + 10, len(legs))
        self.assertEqual((0, 30, 1.5, ean36, False), legs[0])
        self.assertEqual((30, 40, 0.5, ean26, False), legs[1])
        self.assertEqual((40, 60, 1, air, False), legs[2])
        self.assertEqual((60, 60, 22, air, False), legs[3])
        self.assertEqual((60, 18, 4.2, air, False), legs[4])

        deco_legs = legs[5::2]
        for s, l in zip(stops, deco_legs):
            self.assertEqual((s.depth, s.depth, s.time, air, True), l)

        self.assertEqual((6, 0, 0.6, air, True), legs[-1])


    def test_dive_legs_overhead_deco(self):
        """
        Test calculating overhead part of a deco dive (first deco stop)
        """
        ean50 = gas(50, 0, depth=22)
        air = gas(21, 0, depth=40)
        gas_list = GasList(air)
        gas_list.deco_gas.append(ean50)

        legs = [
            (0, 40, 2, air, False),
            (40, 40, 20, air, False),
            (40, 24, 5, air, False), # up to first deco stop
            (24, 24, 1, air, True),
            (24, 21, 1, air, True),
            (21, 21, 1, ean50, True),
            # ...
            (9, 9, 1, ean50, True),
            (9, 9, 1, ean50, True),
            (9, 6, 1, ean50, True),
            # ...
        ]
        oh_legs = dive_legs_overhead(gas_list, legs)
        self.assertEqual(legs[:3], oh_legs)


    def test_dive_legs_overhead_no_deco(self):
        """
        Test calculating overhead part of a deco dive (no deco gas mix)
        """
        air = gas(21, 0, depth=40)
        gas_list = GasList(air)

        legs = [
            (0, 40, 2, air, False),
            (40, 40, 20, air, False),
            (40, 24, 5, air, False), # up to first deco stop
            (24, 24, 1, air, True),
            (24, 21, 1, air, True),
            (21, 21, 1, air, True),
            # ...
            (9, 9, 1, air, True),
            (9, 9, 1, air, True),
            (9, 6, 1, air, True),
            # ...
        ]
        oh_legs = dive_legs_overhead(gas_list, legs)
        self.assertEqual(legs[:3], oh_legs)


    def test_dive_legs_overhead_switch(self):
        """
        Test calculating overhead part of a deco dive (gas mix switch)
        """
        ean50 = gas(50, 0, depth=22)
        air = gas(21, 0, depth=40)
        gas_list = GasList(air)
        gas_list.deco_gas.append(ean50)

        legs = [
            (0, 40, 2, air, False),
            (40, 40, 20, air, False),
            (40, 22, 5, air, False),
            (22, 9, 2, ean50, False), # up to first gas mix switch
            (9, 9, 1, ean50, True),
            (9, 6, 1, ean50, True),
            (6, 6, 3, ean50, True),
            (6, 0, 1, ean50, True),
        ]
        oh_legs = dive_legs_overhead(gas_list, legs)
        self.assertEqual(legs[:3], oh_legs)



class GasMixConsumptionTestCase(unittest.TestCase):
    """
    Gas mix consumption tests.
    """
    def test_gas_volume(self):
        """
        Test gas volume calculation
        """
        air = gas(21, 0)
        ean50 = gas(50, 0, depth=22)
        gas_list = GasList(air)
        gas_list.deco_gas.append(ean50)

        legs = [
            (0, 40, 2, air, False),   # 3b * 2min * 30min/l = 180l
            (40, 40, 20, air, False), # 5b * 20min * 30min/l = 3000l
            (40, 22, 5, air, False),  # 4.1b * 5min * 30min/l = 615l
            (22, 9, 2, ean50, False), # 2.55b * 2min * 30min/l = 153l
            (9, 9, 1, ean50, True),   # 1.9b * 1min * 30min/l = 57l
            (9, 6, 1, ean50, True),   # 1.75b * 1min * 30min/l = 52.5l
            (6, 6, 3, ean50, True),   # 1.6b * 3min  * 30min/l = 144l
            (6, 0, 1, ean50, True),   # 1.3b * 1min * 30min/l = 39l
        ]

        cons = gas_volume(gas_list, legs, 30)

        self.assertEqual(2, len(cons))
        self.assertEqual(3795, cons['Air'])
        self.assertEqual(445.5, cons['EAN50'])


    def test_min_bottom_gas(self):
        """
        Test minimal volume of bottom gas calculation
        """
        air = gas(21, 0)
        ean50 = gas(50, 0, depth=22)
        gas_list = GasList(air)
        gas_list.deco_gas.append(ean50)

        legs = [
            (0, 40, 2, air, False),   # 3b * 2min * 30min/l = 180l
            (40, 40, 20, air, False), # 5b * 20min * 30min/l = 3000l
            (40, 22, 5, air, False),  # 4.1b * 5min * 30min/l = 615l
            (22, 9, 2, ean50, False), # 2.55b * 2min * 30min/l = 153l
            (9, 9, 1, ean50, True),   # 1.9b * 1min * 30min/l = 57l
            (9, 6, 1, ean50, True),   # 1.75b * 1min * 30min/l = 52.5l
            (6, 6, 3, ean50, True),   # 1.6b * 3min  * 30min/l = 144l
            (6, 0, 1, ean50, True),   # 1.3b * 1min * 30min/l = 39l
        ]

        vol = min_gas_volume(gas_list, legs, 30)

        self.assertEqual(3795 * 1.5, vol['Air'])
        self.assertEqual(445.5 * 1.5, vol['EAN50'])


    def test_gas_vol_info(self):
        """
        Test gas volume requirements analysis
        """
        air = gas(21, 0)
        ean50 = gas(50, 0, depth=22)

        mixes = (air, 2000), (ean50, 100)
        gas_vol = OrderedDict(mixes)

        mixes = (air, 2000), (ean50, 100)
        min_gas_vol = OrderedDict(mixes)

        info = gas_vol_info(gas_vol, min_gas_vol)
        self.assertEqual(info[0], 'Gas mix Air volume OK.')
        self.assertEqual(info[1], 'Gas mix EAN50 volume OK.')


    def test_gas_vol_info_warn(self):
        """
        Test gas volume requirements analysis (warning)
        """
        air = gas(21, 0)
        ean50 = gas(50, 0, depth=22)

        mixes = (air, 2000), (ean50, 100)
        gas_vol = OrderedDict(mixes)

        mixes = (air, 1999), (ean50, 99)
        min_gas_vol = OrderedDict(mixes)

        info = gas_vol_info(gas_vol, min_gas_vol)
        self.assertEqual(info[0], 'WARN: Gas mix Air volume NOT OK.')
        self.assertEqual(info[1], 'WARN: Gas mix EAN50 volume NOT OK.')


# vim: sw=4:et:ai
