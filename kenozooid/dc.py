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
Dive computer functionality.
"""

import lxml.etree as et
from datetime import datetime
import logging

import kenozooid.uddf as ku

log = logging.getLogger('kenozooid.dc')

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
            '{0.dc_id}, {0.dc_model}, {0.datetime}'.format(dump))

    drv = _mem_dump(dump.dc_model)
    _save_dives(drv, dump.datetime, dump.data, fout)


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
    ddn = ku.create_dump_data(dout, dc_id=dc_id, datetime=time, data=data)
    dump = ku.dump_data(ddn)

    # convert raw data into dive data and store in output file
    dnodes = drv.dives(dump)
    _, rg = ku.create_node('uddf:profiledata/uddf:repetitiongroup',
            parent=dout)
    for n in dnodes:
        *_, l = ku.create_node('uddf:informationafterdive' \
                '/uddf:equipmentused/uddf:link', parent=n)
        l.set('ref', dc_id)
        rg.append(n)
    
    ku.reorder(dout)
    ku.save(dout, fout)


# vim: sw=4:et:ai
