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
Decompression dive planning.
"""

from collections import namedtuple
import itertools
import math
import operator
import re
import logging

from kenozooid.data import gas
from kenozooid.calc import mod

logger = logging.getLogger(__name__)


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


class DivePlanError(Exception):
    """
    Dive planner exception.
    """



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

    Dive plan information contains list of dive profiles, gas volume
    information and dive decompression parameters.

    :var profiles: List of dive profiles.
    :var min_gas_vol: Minimal volume of gas mixes required for the plan.
    :var last_stop_6m: True if last stop is at 6m.
    :var gf_low: Gradient factor low value (decompression model specific).
    :var gf_high: Gradient factor high value (decompression model specific).
    :var descent_rate: Descent rate.
    :var rmv: Respiratory Minute Volume.
    :var ext_profile: Tuple depth and time to add for an extended dive
        profile.
    """
    def __init__(self):
        self.profiles = []
        self.min_gas_vol = {}
        self.last_stop_6m = False
        self.gf_low = 30
        self.gf_high = 85

        self.descent_rate = 20
        self.rmv = 20
        self.ext_profile = 5, 3

        self.gas_mix_ppo2 = 1.4
        self.deco_gas_mix_ppo2 = 1.6



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
    :var gas_vol: Dictionary of gas mix and gas volume required for the
        dive.
    :var gas_info: Gas mix requirements information.
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
        self.gas_vol = {}
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



def plan_deco_dive(plan, gas_list, depth, time):
    """
    Plan decompression dive.

    The dive plan information is calculated and stored in the dive plan
    object.

    Any dive plan configuration should be set in the dive plan object
    before calling this function.

    :param plan: Dive plan object to be filled with dive plan information.
    :param gas_list: Gas mix configuration list.
    :param depth: Maximum dive depth.
    :param time: Dive bottom time.
    """
    ext_depth = depth + plan.ext_profile[0]
    ext_time = time + plan.ext_profile[1]

    gas_list = gas_mix_depth_update(
        gas_list, plan.gas_mix_ppo2, plan.deco_gas_mix_ppo2
    )

    lost_gas_list = GasList(gas_list.bottom_gas)
    lost_gas_list.travel_gas.extend(gas_list.travel_gas)

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

    for p in plan.profiles:
        stops = deco_stops(plan, p)
        if not stops:
            raise DivePlanError('NDL dive, no plan calculated')

        legs = dive_legs(p, stops, plan.descent_rate)
        if p.type == ProfileType.PLANNED:
            plan.min_gas_vol = min_gas_volume(p.gas_list, legs, rmv=plan.rmv)

        p.deco_time = sum_deco_time(legs)
        p.dive_time = sum_dive_time(legs)
        p.slate = dive_slate(p, stops, legs, plan.descent_rate)

        p.descent_time  = depth_to_time(0, p.depth, plan.descent_rate)
        p.gas_vol = gas_volume(p.gas_list, legs, rmv=plan.rmv)

        # after ver. 0.15
        # if p.type != ProfileType.PLANNED:
        #     p.gas_info = gas_vol_info(p.gas_vol, plan.min_gas_vol)

    assert plan.min_gas_vol


def deco_stops(plan, profile):
    """
    Calculate decompression stops for a dive profile.

    The dive plan information is used to configure decompression engine.

    :param plan: Dive plan information.
    :param profile: Dive profile information.
    """
    import decotengu # configurable in the future, do not import globally
    engine = decotengu.create()
    engine.last_stop_6m = plan.last_stop_6m
    engine.model.gf_low = plan.gf_low / 100
    engine.model.gf_high = plan.gf_high / 100

    gas_list = profile.gas_list

    # add gas mix information to decompression engine
    for m in gas_list.travel_gas:
        engine.add_gas(m.depth, m.o2, m.he, travel=True)
        logger.debug('added travel gas {}'.format(m))

    m = gas_list.bottom_gas
    engine.add_gas(m.depth, m.o2, m.he)
    logger.debug('added bottom gas {}'.format(m))

    for m in gas_list.deco_gas:
        engine.add_gas(m.depth, m.o2, m.he)
        logger.debug('added deco gas {}'.format(m))

    list(engine.calculate(profile.depth, profile.time))

    return engine.deco_table


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
    max_depth = profile.depth
    time = profile.time

    legs = []

    # start with descent
    if gas_list.travel_gas:
        # add dive legs when travel gas mixes are used
        mixes = gas_list.travel_gas + [gas_list.bottom_gas]
        depths = [m.depth for m in mixes[1:]]
        times = (
            depth_to_time(d, m.depth, descent_rate)
            for m, d in zip(mixes, depths)
        )
        legs.extend(
            (m.depth, d, t, m, False)
            for m, d, t in zip(mixes, depths, times)
        )

    # descent leg to max depth, it is always from bottom gas mix switch
    # depth (with or without travel gas mixes), skip it if bottom gas mix
    # to be switched at max depth
    m = gas_list.bottom_gas
    if max_depth > m.depth:
        t = depth_to_time(m.depth, max_depth, descent_rate)
        legs.append((m.depth, max_depth, t, m, False))

    assert abs(sum(l[2] for l in legs) - max_depth / descent_rate) < 0.00001

    # max depth leg, exclude descent time
    t = time - max_depth / descent_rate
    legs.append((max_depth, max_depth, t, gas_list.bottom_gas, False))

    first_stop = stops[0]

    # ascent without decompression stops
    mixes = [m for m in gas_list.deco_gas if m.depth > first_stop.depth]
    depths = [max_depth] + [m.depth for m in mixes] + [first_stop.depth]
    rd = zip(depths[:-1], depths[1:])
    mixes.insert(0, gas_list.bottom_gas)
    legs.extend(
        (d1, d2, (d1 - d2) / 10, m, False)
        for (d1, d2), m in zip(rd, mixes)
    )

    # ascent with decompression stops till the surface
    depths = [s.depth for s in stops[1:]] + [0]
    mixes = {
        (m.depth // 3) * 3: m for m in gas_list.deco_gas
        if m.depth <= first_stop.depth
    }
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
    mix = gas_list.deco_gas[0] if gas_list.deco_gas else None
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
    rt = 0

    # travel gas switches
    k = len(gas_list.travel_gas)
    if k:
        for i in range(k + 1):
            leg = legs[i]

            d = leg[0]
            m = leg[3]
            slate.append((d, None, round(rt), m))
            rt += leg[2]

        legs = legs[k:]

    # bottom time, no descent row on slate
    rt += legs[0][2] + legs[1][2] # reset run-time
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
    if no_deco:
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


def gas_vol_info(gas_vol, min_gas_vol):
    """
    Analyze gas volume requirements using gas mix volume calculations.

    The list of messages is returned, which confirm required gas mix volume
    or warn about gas logistics problems.

    :param gas_vol: Gas volume requirements per gas mix.
    :param min_gas_vol: Minimal gas mixes volume for the plan.

    .. seealso::

       :py:func:`min_gas_volume`
       :py:func:`gas_volume`

    """
    info = []
    for mix, vol in gas_vol.items():
        assert mix in min_gas_vol

        fmt = '{}Gas mix {} volume {}.'
        if vol <= min_gas_vol[mix]:
            msg = fmt.format('', mix.name, 'OK')
        else:
            msg = fmt.format('WARN: ', mix.name, 'NOT OK')
        info.append(msg)

    # TODO: msg = 'No diving cylinders specified to verify its configuration.'
    return info


def gas_volume(gas_list, legs, rmv=20):
    """
    Calculate dive gas mix volume information.

    Gas mix volume is calculated for each gas mix on the gas list. The
    volume information is returned as dictionary `gas mix name -> usage`,
    where gas usage is volume of gas in liters.

    The key of the gas mix volume dictionary is gas mix name to merge all
    travel and decompression gas mixes information regardless their depth
    switch.

    FIXME: apply separate RMV for decompression gas

    :param gas_list: Gas list information.
    :param legs: List of dive legs.
    :param rmv: Respiratory minute volume (RMV) [min/l].

    ..seealso:: :py:func:`dive_legs`
    """
    mixes = gas_list.travel_gas + [gas_list.bottom_gas] + gas_list.deco_gas
    gas_vol = {m.name: 0 for m in mixes}

    items = (
        (leg[3].name, ((leg[0] + leg[1]) / 2 / 10 + 1) * leg[2] * rmv)
        for leg in legs
    )
    key = operator.itemgetter(0)
    items = sorted(items, key=key)
    items = itertools.groupby(items, key)
    gas_vol.update({m: sum(v[1] for v in vols) for m, vols in items})
    return gas_vol


def min_gas_volume(gas_list, legs, rmv=20):
    """
    Calculate minimal volume of gas mixes required for a dive using rule of
    thirds.

    The volume information is returned as dictionary `gas mix -> usage`,
    where gas usage is volume of gas in liters.

    :param gas_list: Gas list information.
    :param legs: List of dive legs.
    """
    # simply take gas volume requirements for the dive
    gas_vol = gas_volume(gas_list, legs, rmv=rmv)

    # but recalculate required volume of bottom gas for overhead part of
    # dive
    oh_legs = dive_legs_overhead(gas_list, legs)
    cons = gas_volume(gas_list, oh_legs, rmv=rmv)
    gas_vol[gas_list.bottom_gas] = cons[gas_list.bottom_gas.name]

    # use rule of thirds
    for mix in gas_vol:
        gas_vol[mix] *= 1.5
    return gas_vol


def gas_mix_depth_update(gas_list, ppo2, deco_ppo2):
    """
    Update gas mix list, so every gas mix has depth specified.

    The following rules are used

    - gas mixes with non-null depth are _not_ changed
    - first travel gas mix switch depth is 0m
    - if no travel gas mixes specified, then bottom gas mix switch depth is
      set to 0m
    - travel and bottom gas mixes are updated with MOD calculated using
      ppO2 and O2 value of previous gas mix on the list
    - decompression gas mixes are updated with MOD calculated using
      decompression ppO2 and O2 value of changed gas mix

    :param gas_list: Gas mix list to modify.
    :param ppo2: ppO2 value used to calculate MOD of travel and bottom gas
        mixes.
    :param deco_ppo2: ppO2 value used to calculate MOD of decompression gas
        mixes.
    """
    def change_gas_mix(gas_mix, o2, ppo2, condition):
        if gas_mix.depth is None:
            v = mod(o2, ppo2) if condition else 0
            return gas_mix._replace(depth=math.floor(v))
        else:
            return gas_mix

    m = gas_list.travel_gas[-1] if gas_list.travel_gas else gas_list.bottom_gas
    bottom_gas = change_gas_mix(
        gas_list.bottom_gas, m.o2, ppo2, gas_list.travel_gas
    )
    new_list = GasList(bottom_gas)

    if gas_list.travel_gas:
        # change first travel gas mix
        m = gas_list.travel_gas[0]
        m = m._replace(depth=0) if m.depth is None else m
        assert m.depth is not None
        new_list.travel_gas = [m]

        o2_list = [m.o2 for m in gas_list.travel_gas]
        new_list.travel_gas.extend(
            change_gas_mix(m, o2, ppo2, True) for m, o2 in
            zip(gas_list.travel_gas[1:], o2_list[:-1])
        )

    new_list.deco_gas = [
        change_gas_mix(m, m.o2, deco_ppo2, True) for m in gas_list.deco_gas
    ]

    return new_list


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
    th = '=' * 30 + ' ' + ' '.join(['=' * 6, ] * 4)
    txt.append(th)
    txt.append(' {:32}'.format('Name') + 'P      E      LG    E+LG')
    txt.append(th)
    for title, attr, fmt in zip(titles, attrs, fmts):
        t = '{:30s} '.format(title) + ' '.join([fmt] * 4)
        values = [getattr(p, attr) for p in plan.profiles]
        txt.append(t.format(*values))
    txt.append(th)
    txt.append('')

    txt.append('')
    t = 'Gas Logistics'
    txt.append(t)
    txt.append('-' * len(t))

    # required gas volume information as a table
    th = '=' * 30 + ' ' + ' '.join(['=' * 6, ] * 4)
    txt.append(th)
    txt.append('{:33s}'.format('Gas Mix') + 'P      E      LG    E+LG')
    txt.append(th)
    gas_list = plan.profiles[0].gas_list # all other plans, do not use more
                                         # gas mixes
    gas_list = gas_list.travel_gas + [gas_list.bottom_gas] + gas_list.deco_gas
    gas_mix_names = sorted(set(m.name for m in gas_list))
    for m in gas_mix_names:
        n = 'Gas Mix {} [liter]'.format(m)
        vol = [p.gas_vol.get(m, 0) for p in plan.profiles]
        # the main profile gas volume reported using rule of thirds
        vol[0] = plan.min_gas_vol[m]
        na = '  xx  '
        s = ('{:6.0f}'.format(v) if v > 0 else na for v in vol)
        t = '{:30s}'.format(n) + ' ' + ' '.join(s)
        txt.append(t)

    txt.append(th)
    txt.append('')

    # after ver. 0.15
    # gas volume analysis information
    # txt.append('')
    # for p in plan.profiles:
    #     if p.type != ProfileType.PLANNED:
    #         txt.append('Dive profile: {}'.format(p.type))
    #         txt.extend('  ' + s for s in p.gas_info)
    # txt.append('')

    # dive slates
    t = 'Dive Slates'
    txt.append(t)
    txt.append('-' * len(t))
    for p in plan.profiles:
        txt.append('Profile *{}*::'.format(p.type))
        txt.append('')
        slate = p.slate
        t = '     {:>3} {:>3} {:>4} {:7}'.format('D', 'DT', 'RT', 'GAS')
        txt.append(t)
        txt.append('    ' + '-' * (len(t) - 1))
        for item in slate:
            st = int(item[1]) if item[1] else ''

            m = item[3]
            star = '*' if m else ' '
            m = m.name if m else ''

            t = '    {}{:>3} {:>3} {:>4} {}'.format(
                star, int(item[0]), st, int(item[2]), m
            )
            txt.append(t)
        txt.append('')

    # dive plan parameters
    t = 'Parameters'
    txt.append(t)
    txt.append('-' * len(t))

    titles = (
        'RMV [l/min]', 'Last stop at 6m', 'GF Low', 'GF High', #'RMV [l/min]', 'Extended Profile',
        #'Decompression Model', 'Decompression Library'
    )
    attrs = ('rmv', 'last_stop_6m', 'gf_low', 'gf_high')#, 'deco_time', 'dive_time')
    fmts = ('{:>6}', ' {}', '{:>6}%', '{:>6}%')#, '{:>6.0f}')#, '{:>6.0f}')
    assert len(titles) == len(fmts) == len(attrs)

    th = '=' * 30 + ' ' + '=' * 7
    txt.append(th)
    txt.append('Parameter' + ' ' * 23 + 'Value')
    txt.append(th)
    for title, attr, fmt in zip(titles, attrs, fmts):
        t = '{:30s} '.format(title) + fmt
        txt.append(t.format(getattr(plan, attr)))
    txt.append(th)
    txt.append('')


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
        depth = None if p is None else int(p)
        #tank = v.group('tank')
        m = gas(o2, he, depth=depth)

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
