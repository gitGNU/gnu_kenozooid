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
Dive logbook functionality.
"""

import lxml.etree as et
from datetime import datetime
from collections import namedtuple
import logging

import kenozooid.uddf as ku

log = logging.getLogger('kenozooid.logbook')

def backup(drv_name, port, fout):
    """
    Backup dive computer data.

    :Parameters:
     drv_name
        Dive computer driver name.
     port
        Dive computer port.
     fout
        Output file.
    """
    drv = _mem_dump(drv_name, port)
    data = drv.dump()
    model = drv.version(data)

    _save_dives(drv, datetime.now(), data, fout)


def convert(drv_name, fin, fout):
    """
    Convert binary dive computer data into UDDF.

    :Parameters:
     drv_name
        Dive computer driver name.
     fin
        Binary dive computer data file name.
     fout
        Output file.
    """
    drv = _mem_dump(drv_name)
    with open(fin, 'rb') as f:
        data = f.read()
        _save_dives(drv, datetime.now(), data, fout)


def extract_dives(fin, fout):
    """
    Extract dives from dive computer dump data.

    :Parameters:
     fin
        UDDF file with dive computer raw data.
     fout
        Output file.
    """
    xp_dc = ku.XPath('//uddf:divecomputerdump')
    
    din = et.parse(fin)
    nodes = xp_dc(din)
    if not nodes:
        raise ValueError('No dive computer dump data found in {}'
                .format(fin))

    assert len(nodes) == 1

    dump = ku.dump_data(nodes[0])

    log.debug('dive computer dump data found: ' \
            '{0.dc_id}, {0.dc_model}, {0.time}'.format(dump))

    drv = _mem_dump(dump.dc_model)
    _save_dives(drv, dump.time, dump.data, fout)


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


def _mem_dump(name, port=None):
    """
    Find memory dump device driver.

    :Parameters:
     name
        Dive computer driver name.
     port
        Dive computer port.
    """
    from kenozooid.driver import MemoryDump, find_driver

    drv = find_driver(MemoryDump, name, port)
    if drv is None:
        raise ValueError('Device driver {} does not support memory dump'
            .format(name))
    return drv


def _save_dives(drv, time, data, fout):
    """
    Convert raw dive computer data into UDDF format and store it in output
    file.

    :Parameters:
     drv
        Dive computer driver used to parse raw data.
     time
        Time of raw dive computer data fetch.
     data
        Raw dive computer data.
     fout
        Output file.
    """
    import kenozooid.uddf as ku
    
    model = drv.version(data)
    log.debug('dive computer version {}'.format(model))

    dout = ku.create()

    # store dive computer information
    xp_owner = ku.XPath('//uddf:diver/uddf:owner')
    dc = ku.create_dc_data(xp_owner(dout)[0], dc_model=model)
    dc_id = dc.get('id')

    # store raw data
    ddn = ku.create_dump_data(dout, dc_id=dc_id, time=time, data=data)
    dump = ku.dump_data(ddn)

    # convert raw data into dive data and store in output file
    dnodes = drv.convert(dump)
    _, rg = ku.create_node('uddf:profiledata/uddf:repetitiongroup',
            parent=dout)
    for n in dnodes:
        equ, l = ku.create_node('uddf:equipmentused/uddf:link')
        l.set('ref', dc_id)
        n.insert(1, equ) # append after datetime element
        rg.append(n)
    
    ku.reorder(dout)
    ku.save(dout, fout)


# vim: sw=4:et:ai
