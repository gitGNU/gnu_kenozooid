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
Dive simulation routines.
"""

import time

def parse(spec):
    """
    Parse dive plan specification.

    Dive plan specification string is a space separated list of dive run
    time and depth values. For example dive plan

    |   RT[min]  | Depth[m] |
    |  1:00      |    10    |
    |  12:20     |    21    |
    |  18:30     |    21    |
    |  40:00     |     5    |
    |  43:00     |     5    |
    |  45:00     |     0    |

    is represented by string as follows::

        1:00,10 12:20,21 18:30,21 40:00,5 43:00,5 45:00,0

    which can be described as

    Run time can be specified in
    
    - seconds, i.e. 15, 20, 3600
    - minutes, i.e. 12:20, 14:00, 67:13

    Depth is always specified in meters.

    Dive plan specification is returned as iterator of runtime and depth
    pairs is returned. Returned runtime is always in seconds since start
    of a dive. Depth is specified in meters.

    :Parameters:
     spec
        Dive plan specification string.
    """
    for chunk in spec.split():
        try:
            t, d = chunk.split(',')
            if ':' in t:
                m, s = map(int, t.split(':'))
                s = min(s, 59)
                t = m * 60 + s
            else:
                t = int(t.strip())
        except:
            raise ValueError('Invalid runtime specification for {}'
                    .format(chunk))

        try:
            d = int(d)
        except:
            raise ValueError('Invalid depth specification for {}'
                    .format(chunk))

        yield t, d


def interpolate(spec):
    """
    Interpolate dive plan times and depths.

    :Parameters:
     spec
        Dive plan specification (as returned by ``parse`` function).

    .. seealso::
        ``parse``
    """
    ptime = 0
    pdepth = 0
    yield ptime, pdepth
    for time, depth in spec:
        count = time - ptime    # interpolation amount
        ddelta = depth - pdepth # depth delta
        value = abs(ddelta)     # value to interpolate

        if value != 0 and count !=0:
            d1 = 1
            d2 = float(ddelta) / count
            # time or depth can be interpolated
            if value <= count:
                value, count = count, value
                d1 = abs(1 / d2)
                if d2 > 0:
                    d2 = 1
                else:
                    d2 = -1

            for i in range(1, count):
                yield int(ptime + d1 * i), int(pdepth + d2 * i)


        yield time, depth

        ptime = time
        pdepth = depth


def simulate(simulator, spec, start=True, stop=True):
    """
    Simulate dive with specified simulator and dive specification.

    :Parameters:
     simulator
        Device driver simulator implementation.
     spec
        Dive plan specification.
     start
        If `False` then simulation is assumed to be started.
     stop
        If `False` then simulation won't be stopped.
    """
    if start:
        simulator.start()
    try:
        # start simulation
        pt, d, *_ = next(spec)
        simulator.depth(d)

        for t, d, *_ in spec:
            time.sleep(t - pt)
            simulator.depth(d)
            pt = t

    finally:
        if stop:
            simulator.stop()

# vim: sw=4:et:ai
