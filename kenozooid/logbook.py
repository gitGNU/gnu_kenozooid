#
# Kenozooid - software stack to support different capabilities of dive
# computers.
#
# Copyright (C) 2009 by Artur Wroblewski <wrobell@pld-linux.org>
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
Dive logbook functionality.
"""

import kenozooid.uddf as ku
from datetime import datetime
from collections import namedtuple

def backup(drv, fout):
    """
    Backup dive computer data.

    :Parameters:
     drv
        Dive computer driver.
     fout
        Output file.
    """
    data = ku.create()

    model = drv.driver.version()
    raw_data = drv.dump()

    # store raw data
    xp_owner = ku.XPath('//uddf:diver/uddf:owner')
    dc = ku.create_dc_data(xp_owner(data)[0], dc_model=model)
    dc_id = dc.get('id')

    Dump = namedtuple('Dump', 'dc_id time data')
    dump = Dump(dc_id, datetime.now(), raw_data)
    ku.create_dump_data(data, **dump._asdict())

    # convert raw data into UDDF
    dive_nodes = drv.convert(dump)
    _, rg = ku.create_node('uddf:profiledata/uddf:repetitiongroup', parent=data)
    for n in dive_nodes:
        equ, l = ku.create_node('uddf:equipmentused/uddf:link')
        l.set('ref', dc_id)
        n.insert(1, equ) # append after datetime element
        rg.append(n)

    ku.reorder(data)
    ku.save(data, fout)


# vim: sw=4:et:ai
