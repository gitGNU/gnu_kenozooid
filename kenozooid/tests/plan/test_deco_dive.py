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
    DiveProfile, DiveProfileType, GasList, GasMix

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
        gas_list = GasList(GasMix(0, 21, 0))
        plan = plan_deco_dive(gas_list, 45, 35)

        self.assertEquals(4, len(plan.profiles))

        t = DiveProfileType
        expected = [t.PLANNED, t.EXTENDED, t.LOST_GAS, t.EXTENDED_LOST_GAS]
        types = [p.type for p in plan.profiles]
        self.assertEquals(expected, types)


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

        gas_list = GasList(GasMix(33, 27, 0))
        gas_list.travel_gas.append(GasMix(0, 32, 0))
        gas_list.deco_gas.append(GasMix(22, 50, 0))
        gas_list.deco_gas.append(GasMix(10, 80, 0))

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
        ean27 = GasMix(33, 27, 0)
        ean50 = GasMix(22, 50, 0)
        ean80 = GasMix(10, 80, 0)

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


# vim: sw=4:et:ai
