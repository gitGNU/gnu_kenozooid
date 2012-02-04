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
Dive computer functionality.
"""

from datetime import datetime
from functools import partial
import lxml.etree as et
import logging

import kenozooid.component as kc
import kenozooid.data as kd
import kenozooid.flow as kf
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
    Find data parser device driver.

    :Parameters:
     name
        Dive computer driver name.
     port
        Dive computer port.
    """
    from kenozooid.driver import DataParser, find_driver

    drv = find_driver(DataParser, name, port)
    if drv is None:
        raise ValueError('Device driver {} does not support data parsing'
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
    model = drv.version(data)
    dc_id = ku.gen_id(model)
    log.debug('dive computer version {}'.format(model))

    # convert raw data into dive data and store in output file
    bdata = kd.BinaryData(datetime=time, data=data)
    
    eq = ku.create_dc_data(dc_id, model)
    dump = ku.create_dump_data(dc_id=dc_id, datetime=time, data=data)

    p = kc.params(drv.__class__)
    if 'gas' in p['data']:
        log.debug('gas data pipeline')
        with kf.buffer_open(2) as (f_g, f_d):

            # store gas and dives in two separate files,
            # then merge the data into one UDDF file
            save = kf.sink(partial(ku.save, fout=fout))
            m = kf.concat(2, partial(cat_gd, equipment=eq, dump=dump), save)
            kf.send(
                kf.pipe(drv.dives(bdata),
                    kd.sort_dives,
                    kd.uniq_dives),
                kf.split(
                    extract_gases(uniq_gases(kf.buffer(f_g, m))),
                    create_dives(kf.buffer(f_d, m), equipment=(dc_id,))
                )
            )

    else:
        log.debug('simple data pipeline')
        dives = kf.pipe(drv.dives(bdata),
                kd.sort_dives,
                kd.uniq_dives,
                partial(ku.create_dives, equipment=(dc_id,)))
        ku.save(ku.create_uddf(equipment=eq, dives=dives, dump=dump), fout)

#
# fixme: put the functions/coroutines below into proper modules
#
@kf.coroutine
def create_dives(tg, equipment=None):
    while True:
        dive = yield
        n = ku.create_dive(dive, equipment=equipment)
        tg.send(n)

@kf.coroutine
def extract_gases(tc):
    while True:
        dive = yield
        for s in dive.profile:
            if s.gas is not None:
                tc.send(s.gas)

@kf.coroutine
def uniq_gases(tc):
    gases = set()
    while True:
        gas = yield
        if gas not in gases:
            gases.add(gas)
            n = ku.create_gas(gas)
            tc.send(n)

def cat_gd(fg, fd, equipment=None, dump=None):
    xfg = xfd = None
    fg.seek(0)
    fd.seek(0)
    if len(fg.read(1)) > 0:
        xfg = ku.xml_file_copy(fg)
    if len(fd.read(1)) > 0:
        xfd = ku.xml_file_copy(fd)
    fg.seek(0)
    fd.seek(0)
    return ku.create_uddf(equipment=equipment,
            dump=dump,
            gases=xfg,
            dives=xfd)

# vim: sw=4:et:ai
