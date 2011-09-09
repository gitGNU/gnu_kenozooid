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
Various calculation methods like partial pressure, equivalent air depth,
maximum operating depth, etc.
"""

import functools

def ppg(depth, ean, gas):
    """
    Calculate partial pressure of a gas.

    :Parameters:
     depth
        Depth in meters.
     ean
        O2 percentage, i.e. 32, 34, 27.5.
     gas
        Gas to be calculated - O2 (oxygen) or N2 (nitrogen).
    """
    if gas not in ('O2', 'N2'):
        raise ValueError('Invalid gas value: '  + gas)

    p = 1.0 + depth / 10.0 # absolute pressure
    fg = ean / 100.0 if gas == 'O2' else 1.0 - ean / 100.0
    
    return p * fg


def mod(ean, pp=1.4):
    """
    Calculate maximum operating depth for specified partial pressure.

    :Parameters:
     ean
        O2 percentage, i.e. 32, 34, 27.5.
     pp
        Maximum partial pressure.
    """
    fg = ean / 100.0 
    p = pp / fg
    return (p - 1) * 10


def ead(depth, ean):
    """
    Calculate equivalent air depth for specified depth and EAN.
    
    :Parameters:
     depth
        Depth in meters.
     ean
        O2 percentage, i.e. 32, 34, 27.5.
    """
    fN = (100.0 - ean) / 100.0
    return (depth + 10.0) * fN / 0.79 - 10.0


def rmv(tank, pressure, depth, duration):
    """
    Calculate respiratory minute volume (RMV).

    :Parameters:
     tank
        Tank size in liters, i.e. 12l, 15l.
     pressure
        Difference in pressure of the tank at the end and start of a dive,
        i.e. 170 (220 at start, 50 at end of a dive).
     depth
        The average depth of a dive.
     duration
        Duration of a dive in minutes.
    """
    return tank * pressure / (depth / 10.0 + 1) / duration


ppN2 = functools.partial(ppg, gas='N2')
ppO2 = functools.partial(ppg, gas='O2')


# vim: sw=4:et:ai
