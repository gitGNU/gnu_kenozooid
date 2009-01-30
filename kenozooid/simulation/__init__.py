#
# Kenozooid - software stack to support OSTC dive computer.
#
# Copyright (C) 2009 by wrobell <wrobell@pld-linux.org>
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

import time
from datetime import datetime

"""
Dive simulation routines.
"""

def parse(spec):
    """
    Parse dive simulation specification.

    Simulation specification string is a space separated list of dive time
    and depth values. For example::

        1:00,10 12:20,21 18:30,21 40:00,5 43:00,5 45:00,0

    Above dive simulation specification can be described

    - diver descents within one minute to 10m
    - descent is carried on to 21m, which is reached at 12 minutes and 20s
      from the start of the dive
    - diver remains at 21m until 18 minutes and 30s of the dive
    - diver descents slowly to 5m, the depth is not reached until 40th
      minute of the dive
    - 3 minutes stop is performed at 5m
    - diver surfaces at 45th minute of the dive

    Time is specified in
    
    - seconds, i.e. 15, 20, 3600
    - minutes, i.e. 12:20, 14:00, 67:13

    Depth is always specified in meteres.

    Iterator of time and depth pairs is returned. Returned time is always
    in seconds since start of a dive. Depth is specified in meteres.

    :Parameters:
     spec
        Simulation specification string.
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
            raise ValueError('Invalid time specification for "%s"' % chunk)

        try:
            d = int(d)
        except:
            raise ValueError('Invalid depth specification for "%s"' % chunk)

        yield t, d


def interpolate(spec):
    """
    Interpolate dive simulation times and depths.

    :Parameters:
     spec
        Specification of dive simulation.
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


def simulate(simulator, spec):
    data = interpolate(tuple(parse(spec)))
    simulator.start()
    try:
        # start simulation
        pt, d = data.next()
        simulator.depth(d)

        for t, d in data:
            time.sleep(t - pt)
            simulator.depth(d)
            pt = t

    finally:
        simulator.stop()
        

class SysOutSimulator(object):
    def start(self):
        print 'start simulator simulation'

    def depth(self, d):
        print '%s -> %02dm' % (datetime.now().time(), d)

    def stop(self):
        print 'stop simulator simulation'


