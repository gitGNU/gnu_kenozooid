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

from collections import namedtuple
from operator import attrgetter

import kenozooid.util as ku

def ntuple(name, fields):
    """
    Create a named tuple with all fields set to ``None`` by default.
    
    :Parameters:
     name
        Name of tuple.
     fields
        String containing space separated list of field names.
    """
    t = namedtuple(name, fields)
    k = len(t._fields)
    df = k * (None, )
    dt = t(*df)
    return dt._replace


Dive = ntuple('Dive', 'datetime depth duration temp avg_depth profile' \
        ' equipment')
Sample = ntuple('Sample', 'depth time temp setpoint setpointby' \
        ' deco_time deco_depth alarm gas')
Gas = ntuple('Gas', 'id name o2 he')
BinaryData = ntuple('BinaryData', 'datetime data')


def gas(o2, he):
    """
    Convert Oxygen and Helium values into Gas data record with id and name.
    """
    id = 'air'
    name = 'Air'
    if o2 == 100:
        id = 'o2'
        name = 'O2'
    elif o2 > 21 and he == 0:
        id = 'ean{:02d}'.format(o2)
        name = 'EAN{:02d}'.format(o2)
    elif he > 0:
        id = 'tx{:02d}{:02d}'.format(o2, he)
        name = 'TX {:02d}/{:02d}'.format(o2, he)
    return Gas(id=id, name=name, o2=o2, he=he)


def sort_dives(dives):
    """
    Sort dives by dive datetime.
    """
    return sorted(dives, key=attrgetter('datetime'))


def uniq_dives(dives):
    """
    Remove duplicated dives from sorted iterator of dives.
    """
    ld = None
    for d in dives:
        if ld != d.datetime:
            yield d
        ld = d.datetime

# vim: sw=4:et:ai
