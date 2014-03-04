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

"""
Decompression dive planning.
"""

import re
from collections import namedtuple

from kenozooid.data import gas
from kenozooid.calc import mod


RE_GAS = re.compile("""
    ^(?P<name>
        (?P<type> O2 | AIR | EAN | TX)
        ((?<=TX|AN)(?P<o2>[0-9]{2}))?
        ((?<=TX..)/(?P<he>[0-9]{2}))?
    )
    (@(?P<depth>[0-9]+))?
    (\|(?P<tank>([2-9]x[1-9]{1,2})))?
    $
""", re.VERBOSE)


class GasList(object):
    """
    List of gas mixes.

    :var travel_gas: List of travel gas mixes.
    :var bottom_gas: Bottom gas mix.
    :var deco_gas: List of decompression gas mixes.
    """
    def __init__(self, gas):
        """
        Create list of gas mixes.

        :param gas: Bottom gas mix.
        """
        self.bottom_gas = gas
        self.travel_gas = []
        self.deco_gas = []



class DivePlan(object):
    """
    Dive plan information.

    :var profiles: List of dive profiles.
    """
    def __init__(self):
        self.profiles = []



class DiveProfile(object):
    """
    Dive profile information.

    :var type: Dive profile type.
    :var gas_list: Gas list for the dive profile.
    :var depth: Maximum dive depth.
    :var time: Dive bottom time.
    :var descent_time: Time required to descent to dive bottom depth.
    :var deco_time: Total decompression time.
    :var dive_time: Total dive time.
    :var slate: Dive slate.
    :var gas_info: Gas mix requirements.
    """
    def __init__(self, type, gas_list, depth, time):
        self.type = type
        self.gas_list = gas_list
        self.depth = depth
        self.time = time
        self.descent_time = 0
        self.deco_time = 0
        self.dive_time = 0
        self.slate = []
        self.gas_info = []



class ProfileType(object):
    """
    Dive profile type.

    The dive profile types are

    PLANNED
        Dive profile planned by a diver.
    EXTENDED
        Extended dive profile compared to planned dive profile.
    LOST_GAS
        Dive profile as planned dive but for lost decompression gas.
    EXTENDED_LOST_GAS
        Combination of `EXTENDED` and `LOST_GAS` dive profiles.
    """
    PLANNED = 'planned'
    EXTENDED = 'extended'
    LOST_GAS = 'lost gas'
    EXTENDED_LOST_GAS = 'extended + lost gas'



def plan_deco_dive(gas_list, depth, time, descent_rate=20, ext=(5, 3)):
    """
    Plan decompression dive.
    """
    ext_depth = depth + ext[0]
    ext_time = time + ext[1]

    lost_gas_list = GasList(gas_list.bottom_gas)
    lost_gas_list.travel_gas.extend(gas_list.travel_gas)

    plan = DivePlan()

    p = DiveProfile(ProfileType.PLANNED, gas_list, depth, time)
    plan.profiles.append(p)

    p = DiveProfile(ProfileType.EXTENDED, gas_list, ext_depth, ext_time)
    plan.profiles.append(p)

    p = DiveProfile(ProfileType.LOST_GAS, lost_gas_list, depth, time)
    plan.profiles.append(p)

    p = DiveProfile(
        ProfileType.EXTENDED_LOST_GAS, lost_gas_list, ext_depth, ext_time
    )
    plan.profiles.append(p)

    bottom_gas_vol = 0 # minimal volume of bottom gas mix
    for p in plan.profiles:
        stops = deco_stops(p)

        legs = dive_legs(p, stops, descent_rate)
        if p.type == ProfileType.PLANNED:
            bottom_gas_vol = min_bottom_gas(p.gas_list, legs)

        p.deco_time = sum_deco_time(legs)
        p.dive_time = sum_dive_time(legs)
        p.slate = dive_slate(p, stops, legs, descent_rate)

        p.gas_info = gas_info(p)
        p.descent_time  = depth_to_time(0, p.depth, descent_rate)

    assert bottom_gas_vol > 0

    return plan


def deco_stops(profile):
    """
    Calculate decompression stops for a dive profile.

    :param profile: Dive profile information.
    """
    import decotengu # configurable in the future, do not import globally
    engine, dt = decotengu.create()

    gas_list = profile.gas_list

    # add gas mix information to decompression engine
    for m in gas_list.travel_gas:
        engine.add_gas(m.depth, m.o2, m.he, travel=True)
    m = gas_list.bottom_gas
    engine.add_gas(m.depth, m.o2, m.he)
    for m in gas_list.deco_gas:
        engine.add_gas(m.depth, m.o2, m.he)

    list(engine.calculate(profile.depth, profile.time))

    return dt.stops


def dive_legs(profile, stops, descent_rate):
    """
    Calculate dive legs information.

    The dive legs information is used for other calculations, i.e. dive gas
    consumption, dive slate.

    Dive profile is split into legs using

    - gas mix switch depths
    - dive maximum depth and bottom time
    - descent rate
    - list of decompression stops

    The ascent rate is assumed to be 10m/min.

    Each dive leg consists of the following information

    - start depth
    - end depth
    - time
    - gas mix used during a dive leg
    - deco zone indicator (true or false)
    """
    gas_list = profile.gas_list
    depth = profile.depth
    time = profile.time

    legs = []

    # start with descent
    if gas_list.travel_gas:
        mixes = gas_list.travel_gas + [gas_list.bottom_gas]
        depths = [m.depth for m in mixes[1:]]
        for m, d in zip(mixes, depths):
            t = depth_to_time(d, m.depth, descent_rate)
            assert t > 0, (m, d, t)
            legs.append((m.depth, d, t, m, False))
    d = legs[-1][1] if legs else 0
    if d != depth:
        t = depth_to_time(depth, d, descent_rate)
        legs.append((d, depth, t, gas_list.bottom_gas, False))

    assert abs(sum(l[2] for l in legs) - depth / descent_rate) < 0.00001

    # max depth leg, exclude descent time
    t = time - depth / descent_rate
    legs.append((depth, depth, t, gas_list.bottom_gas, False))

    # deco free ascent
    fs = stops[0]
    mixes = [m for m in gas_list.deco_gas if m.depth > fs.depth]
    depths = [depth] + [m.depth for m in mixes] + [fs.depth]
    rd = zip(depths[:-1], depths[1:])
    mixes.insert(0, gas_list.bottom_gas)
    for (d1, d2), m in zip(rd, mixes):
        assert d1 > d2, (d1, d2)
        t = (d1 - d2) / 10
        legs.append((d1, d2, t, m, False))

    # deco ascent
    depths = [s.depth for s in stops[1:]] + [0]
    mixes = {(m.depth // 3) * 3: m for m in gas_list.deco_gas if m.depth <= fs.depth}
    cm = legs[-1][3] # current gas mix
    for s, d in zip(stops, depths):
        cm = mixes.get(s.depth, cm) # use current gas mix until gas mix switch
        legs.append((s.depth, s.depth, s.time, cm, True))
        t = (s.depth - d) / 10
        legs.append((s.depth, d, t, cm, True))

    return legs


def dive_legs_overhead(gas_list, legs):
    """
    Determine the overhead part of a decompression dive.

    The overhead part of a dive is the descent, bottom and ascent parts of
    a dive up to first decompression stop or first decompression gas mix
    switch.

    The overhead part of a dive is used to calculate gas mix consumption
    using rule of thirds.

    :param gas_list: Gas list information.
    :param legs: List of dive legs.

    ..seealso:: :py:func:`dive_legs`
    """
    mix = gas_list.deco_gas[0]
    nr = range(len(legs))
    k = next(k for k in nr if legs[k][3] == mix or legs[k][-1])
    return legs[:k]


def dive_slate(profile, stops, legs, descent_rate):
    """
    Calculate dive slate for a dive profile.

    The dive decompression stops is a collection of items implementing the
    following interface

    depth
        Depth of dive stop [m].
    time
        Time of dive stop [min].

    Dive slate is list of items consisting of

    - dive depth
    - decompression stop information, null if no decompression
    - run time in minutes
    - gas mix on gas switch, null otherwise

    :param profile: Dive profile information.
    :param stops: Dive decompression stops.
    :param legs: Dive legs.
    :param descent_rate: Dive descent rate.
    """
    slate = []

    depth = profile.depth
    time = profile.time
    gas_list = profile.gas_list

    # travel gas switches
    k = len(gas_list.travel_gas)
    if k:
        k += 1
        rt = 0
        for i in range(k):
            leg = legs[i]

            d = leg[0]
            m = leg[3]
            slate.append((d, None, round(rt), m))
            rt += leg[2]

        legs = legs[k:]

    # bottom time, no descent row on slate
    rt = legs[0][2] + legs[1][2] # reset run-time
    d = legs[1][0]
    m = None if gas_list.travel_gas else legs[1][3]
    slate.append((d, None, round(rt), m))

    # no deco gas switches
    no_deco = [l for l in legs if not l[4]]
    no_deco = no_deco[2:]
    for i in range(1, len(no_deco)):
        prev = no_deco[i - 1]
        leg = no_deco[i]

        d = leg[0]
        rt += prev[2]
        m = leg[3]
        slate.append((d, None, round(rt), m))

    # decompression stops
    deco = [l for l in legs if l[4]]
    deco.insert(0, no_deco[-1])
    for i in range(1, len(deco), 2):
        prev = deco[i - 1]
        leg = deco[i]

        d = leg[1]
        dt = leg[2]
        rt += dt + prev[2]
        m = None if prev[3] == leg[3] else leg[3] # indicate gas switch only
        slate.append((d, dt, round(rt), m))

    # surface
    leg = deco[-1]
    d = leg[1]
    rt += leg[2]
    slate.append((d, None, round(rt), None))

    return slate


def depth_to_time(start, end, rate):
    """
    Calculate time required to descent or ascent from start to end depth.

    :param start: Starting depth.
    :param end: Ending depth.
    :param rate: Ascent or descent rate.
    """
    return abs(start - end) / rate


def sum_deco_time(legs):
    """
    Calculate total decompression time using dive legs.

    :param legs: List of dive legs.

    ..seealso:: :py:func:`dive_legs`
    """
    return sum(l[2] for l in legs if l[-1])


def sum_dive_time(legs):
    """
    Calculate total dive time using dive legs.

    :param legs: List of dive legs.

    ..seealso:: :py:func:`dive_legs`
    """
    return sum(l[2] for l in legs)


def gas_info(profile):
    """
    Calculate gas requirements information.

    :param profile: Dive profile information.
    """
    info = []
    return info


def gas_consumption(gas_list, legs, rmv=20):
    """
    Calculate gas mix consumption information.

    Gas mix consumption is calculated for each gas mix on the gas list.
    The consumption information is returned as dictionary `gas mix -> usage`,
    where gas usage is volume of gas in liters.

    FIXME: apply separate RMV for decompression gas

    :param gas_list: Gas list information.
    :param legs: List of dive legs.
    :param rmv: Respiratory minute volume (RMV) [min/l].

    ..seealso:: :py:func:`dive_legs`
    """
    cons = {m: 0 for m in gas_list.travel_gas}
    cons[gas_list.bottom_gas] = 0
    cons.update({m: 0 for m in gas_list.deco_gas})
    for leg in legs:
        d = (leg[0] + leg[1]) / 2
        t = leg[2]
        m = leg[3]
        cons[m] += (d / 10 + 1) * t * rmv

    return cons


def min_bottom_gas(gas_list, legs, rmv=20):
    """
    Calculate minimal volume of bottom gas required for a dive using rule
    of thirds.

    :param gas_list: Gas list information.
    :param legs: List of dive legs.
    """
    bottom_gas = gas_list.bottom_gas

    # calculate required gas for overhead part of a dive
    oh_legs = dive_legs_overhead(gas_list, legs)
    cons = gas_consumption(gas_list, oh_legs, rmv=rmv)
    vol = cons[bottom_gas]

    # use rule of thirds
    return vol * 1.5


def plan_to_text(plan):
    """
    Convert decompression dive plan to text.
    """
    txt = []

    # dive profiles summary
    txt.append('')
    t = 'Dive Profile Summary'
    txt.append(t)
    txt.append('-' * len(t))

    titles = (
        'Depth [m]', 'Bottom Time [min]', 'Descent Time [min]',
        'Total Decompression Time [min]', 'Total Dive Time [min]',
    )
    attrs = ('depth', 'time', 'descent_time', 'deco_time', 'dive_time')
    fmts = ('{:>6d}', '{:>6d}', '{:>6.1f}', '{:>6.0f}', '{:>6.0f}')
    assert len(titles) == len(fmts) == len(attrs)

    # create dive profiles summary table
    th = '-' * 30 + ' ' + ' '.join(['-' * 6, ] * 4)
    txt.append(th)
    txt.append(' ' * 33 + 'P      E      LG    E+LG')
    txt.append(th)
    for title, attr, fmt in zip(titles, attrs, fmts):
        t = '{:30s} '.format(title) + ' '.join([fmt] * 4)
        values = [getattr(p, attr) for p in plan.profiles]
        txt.append(t.format(*values))

    txt.append(th)

    # dive slates
    for p in plan.profiles:
        txt.append('')

        t = 'Slate: {}'.format(p.type)
        txt.append(t)
        txt.append('-' * len(t))

        slate = p.slate
        t = ' {:>3} {:>3} {:>4} {:7}'.format('D', 'DT', 'RT', 'GAS')
        txt.append(t)
        txt.append(' ' + '-' * (len(t) - 1))
        for item in slate:
            st = int(item[1]) if item[1] else ''

            m = item[3]
            star = '*' if m else ' '
            m = m.name if m else ''

            t = '{}{:>3} {:>3} {:>4} {}'.format(
                star, int(item[0]), st, int(item[2]), m
            )
            txt.append(t)

    return '\n'.join(txt)


def parse_gas(t, travel=False):
    """
    Parse gas mix.

    :param t: Gas mix string.
    :param travel: True if travel gas mix.
    """
    t = t.upper()
    v = RE_GAS.search(t)
    m = None

    if v:
        n = v.group('name')

        p = v.group('o2')
        if p is None:
            if n == 'AIR':
                o2 = 21
            elif n == 'O2':
                o2 = 100
            else:
                return None
        else:
            o2 = int(p)

        p = v.group('he')
        he = 0 if p is None else int(p)

        p = v.group('depth')
        depth = mod(o2, 1.6) if p is None else int(p)
        #tank = v.group('tank')
        m = gas(o2, he, depth=int(depth))

    return m


def parse_gas_list(*args):
    """
    Parse gas mix list.

    :param *args: List of gas mix strings.
    """
    travel_gas = [parse_gas(a[1:], True) for a in args if a[0] == '+']
    deco_gas = [parse_gas(a) for a in args if a[0] != '+']
    bottom_gas = deco_gas[0]
    del deco_gas[0]

    gl = GasList(bottom_gas)
    gl.travel_gas.extend(travel_gas)
    gl.deco_gas.extend(deco_gas)
    return gl


# vim: sw=4:et:ai
