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

import lxml.etree as et
from datetime import datetime
from collections import namedtuple
import logging

import kenozooid.uddf as ku

log = logging.getLogger('kenozooid.logbook')

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


def extract_dives(fin, fout):
    """
    Extract dives from dive computer dump data.

    :Parameters:
     fin
        File with dive computer dump data.
     fout
        Output file.
    """
    from kenozooid.driver import MemoryDump, find_driver
    import kenozooid.uddf as ku
    
    dout = ku.create()
    
    xp_dc = ku.XPath('//uddf:divecomputerdump')
    xp_owner = ku.XPath('//uddf:diver/uddf:owner')
    
    din = et.parse(fin)
    nodes = xp_dc(din)

    if not nodes:
        raise ValueError('No dive computer dump data found in ' + fin)

    assert len(nodes) == 1

    dump = ku.dump_data(nodes[0])

    log.debug('dive computer dump data found: ' \
            '{0.dc_id}, {0.dc_model}, {0.time}'.format(dump))

    dc = ku.create_dc_data(xp_owner(dout)[0], dc_model=dump.dc_model)
    dc_id = dc.get('id')
    dump = dump._replace(dc_id=dc_id, data=dump.data)

    ku.create_dump_data(dout, dc_id=dc_id, time=dump.time, data=dump.data)

    # determine device driver to parse the dump and convert dump
    # data into UDDF profile data
    dumper = find_driver(MemoryDump, dump.dc_model, None)
    dnodes = dumper.convert(dump)
    _, rg = ku.create_node('uddf:profiledata/uddf:repetitiongroup',
            parent=dout)
    for n in dnodes:
        equ, l = ku.create_node('uddf:equipmentused/uddf:link')
        l.set('ref', dc_id)
        n.insert(1, equ) # append after datetime element
        rg.append(n)
    
    ku.reorder(dout)
    ku.save(dout, fout)



def add_dive(fout, time=None, depth=None, duration=None, dive_no=None, fin=None):
    """
    Add new dive to logbook file.

    The logbook file is created if it does not exist.

    :Parameters:
     fout
        Logbook file.
     time
        Dive time.
     depth
        Dive maximum depth.
     duration
        Dive duration (in minutes).
     dive_no
        Dive number in dive profile file.
     fin
        Dive profile file.
    """
    dive = None # obtained from profile file

    if os.path.exists(fout):
        doc = et.parse(fout).getroot()
    else:
        doc = ku.create()

    if dive_no is not None and fin is not None:
        q = ku.XPath('//uddf:dive[position() = $no]')
        dives = ku.parse(fin, q, no=no)
        dive = next(dives, None)
        if dive is None:
            raise ValueError('Cannot find dive in UDDF profile data')
        if next(dives, None) is not None:
            raise ValueError('Too many dives found')

    elif time is not None and depth is not None and duration is not None:
        duration = int(duration * 3600)
    else:
        raise ValueError('Dive data or dive profile needs to be provided')

    if dive is not None:
        if time is None:
            time = ku.xp(dive, 'datetime/text()')
        if depth is None:
            depth = ku.xp(dive, 'greatestdepth/text()')
        if duration is None:
            duration = ku.xp(dive, 'diveduration/text()')
            
            
    ku.create_dive_data(doc, time=time, depth=depth,
            duration=duration)

    if dive is not None:
        _, rg = ku.create_node('uddf:profiledata/uddf:repetitiongroup',
                parent=doc)
        rg.append(deepcopy(dive))
    ku.reorder(doc)
    ku.save(doc, fout)


# vim: sw=4:et:ai
