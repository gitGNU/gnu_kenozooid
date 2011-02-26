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
OSTC dive computer binary data parsing routines.
"""

import logging
import re
from collections import namedtuple
from struct import unpack, calcsize
from binascii import hexlify

log = logging.getLogger('kenozooid.driver.ostc')

# command 'a' output
StatusDump = namedtuple('StatusDump', 'preamble eeprom voltage ver1 ver2 profile')
FMT_STATUS = '<6s256sHbb32768s'
LEN_STATUS = calcsize(FMT_STATUS)

# profile data is FA0FA..(43)..FBFB...FDFD
RE_PROFILE = re.compile(b'(\xfa\xfa.{43}\xfb\xfb)(.+?\xfd\xfd)', re.DOTALL)

# dive profile header
DiveHeader = namedtuple('DiveHeader', """\
start version month day year hour minute max_depth dive_time_m dive_time_s
min_temp surface_pressure desaturation gas1 gas2 gas3 gas4 gas5 gas6 gas
ver1 ver2 voltage sampling div_temp div_deco div_tank div_ppo2
div_deco_debug div_res2 spare end
""")
FMT_DIVE_HEADER = '<H6BHHB' 'HHH6HB' 'BBHB4B' 'BBHH'

# dive profile data block sample
DiveSample = namedtuple('DiveSample', 'depth alarm gas_set_o2 gas_set_he'
    ' current_gas temp deco_depth deco_time tank ppo2')


def status(data):
    """
    Split status and profile data, see `StatusDump` named tuple.
    """
    dump = StatusDump._make(unpack(FMT_STATUS, data[:LEN_STATUS]))
    log.debug('unpacked status dump, voltage %d, version %d.%d'
        % (dump.voltage, dump.ver1, dump.ver2))
    return dump


def profile(data):
    """
    Split profile data into individual dive profiles using profile
    regular expression `RE_PROFILE`.

    Collection of tuples (header, block) is returned

     header
        dive profile header 
     block 
        dive profile block data

    """
    return RE_PROFILE.findall(data)


def header(data):
    """
    Parse OSTC dive profile header, see `DiveHeader` named tuple.
    """
    header = DiveHeader._make(unpack(FMT_DIVE_HEADER, data))
    log.debug('parsed dive header {0.year:>02d}/{0.month:>02d}/{0.day:>02d}' \
        ' {0.hour:>02d}:{0.minute:>02d}' \
        ' max depth={0.max_depth}'.format(header))
    return header


def dive_data(header, data):
    """
    Parse OSTC dive profile data block.
    """
    div_temp_s, div_temp_c = divisor(header.div_temp)
    div_deco_s, div_deco_c = divisor(header.div_deco)
    div_tank_s, div_tank_c = divisor(header.div_tank)
    div_ppo2_s, div_ppo2_c = divisor(header.div_ppo2)
    div_deco_debug_s, div_deco_debug_c = divisor(header.div_deco_debug)

    log.debug('header divisor values %x %x %x %x %x' % (header.div_temp,
        header.div_deco, header.div_tank, header.div_ppo2,
        header.div_deco_debug))

    dive_total_time = header.dive_time_m * 60 + header.dive_time_s

    i = 0
    j = 1 # sample number 
    while i < len(data) - 2: # skip profile block data end
        depth = unpack('<H', data[i:i + 2])[0] / 100.0
        i += 2

        # size is count of bytes after profile byte
        pfb = data[i]
        i += 1
        size, event = flag_byte(pfb)
        log.debug('sample %d info: depth = %.2f, pfb = %s, %s',
                j, depth, hex(pfb), hexlify(data[i:i+size]))

        alarm = None
        gas_set = 0
        gas_set_o2 = None
        gas_set_he = None
        gas_change = 0
        current_gas = None
        # parse event byte information
        if event:
            v = data[i]
            i += 1
            alarm = v & 0x0f
            gas_set = v & 0x10
            gas_change = v & 0x20

            if gas_set:
                gas_set_o2 = data[i]
                gas_set_he = data[i + 1]
                i += 2
                gas_set = 2

            if gas_change:
                current_gas = data[i]
                i += 1
                gas_change = 1

        div_bytes = 0

        temp = sample_data(data, i, j, div_temp_s, div_temp_c)
        if temp is not None:
            assert len(temp) == div_temp_c == 2
            temp = unpack('<H', temp)[0] / 10.0
            i += div_temp_c
            div_bytes += div_temp_c

        deco = sample_data(data, i, j, div_deco_s, div_deco_c)
        if deco is not None:
            assert len(deco) == div_deco_c
            deco_depth, deco_time = deco
            i += div_deco_c
            div_bytes += div_deco_c
            log.debug('deco time %d, depth %d' % (deco_time, deco_depth))
        else:
            deco_depth, deco_time = None, None

        tank = sample_data(data, i, j, div_tank_s, div_tank_c)
        if tank is not None:
            i += div_tank_c
            div_bytes += div_tank_c

        ppo2 = sample_data(data, i, j, div_ppo2_s, div_ppo2_c)
        if ppo2 is not None:
            i += div_ppo2_c
            div_bytes += div_ppo2_c
            log.debug('ppo2 %d' % ppo2)

        deco_debug = sample_data(data, i, j, div_deco_debug_s, div_deco_debug_c)
        if deco_debug is not None:
            i += div_deco_debug_c
            div_bytes += div_deco_debug_c
            
        if size != event + gas_set + gas_change + div_bytes:
            log.debug('invalid dive data, sample = %d, depth = %.2f, pfb = 0x%x, size = %d, event = %d,' \
                ' alarm = %s, temp = %s, gas_set = %d, gas_change = %d,' \
                ' div_bytes = %d, deco_debug = %s' \
                    % (j, depth, pfb, size, event, alarm, temp, gas_set,
                            gas_change, div_bytes,
                            hexlify(deco_debug if deco_depth else b'[]')))
            raise ValueError('Invalid dive')

        # is a sample within dive total time? if not, then skip sample
        if header.sampling * (j - 1) <= dive_total_time:
            yield DiveSample(depth, alarm, gas_set_o2, gas_set_he, current_gas,
                    temp, deco_depth, deco_time, tank, ppo2)
        else:
            log.debug('skipped sample %d (out of dive time), seek %d' % (j, i))
        j += 1

    assert data[i:i + 2] == b'\xfd\xfd'


def sample_data(data, i, sample, div_sample, div_count):
    """
    Parse sample item like temperature, deco, etc.

    :Parameters:
     data
        Profile block data.
     i
        Profile block data index, where sample item can be found.
     sample
        Number of dive sample (starts from 1).
     div_sample
        Divisor sampling information.
     div_count
        Sample item data byte count.
    """
    v = None
    if div_sample and sample % div_sample == 0:
        v = data[i:i + div_count]
    return v


def divisor(value):
    """
    Split divisor value into divisor sample information and divisor
    byte count.
    """
    return value & 0b1111, value >> 4


def flag_byte(value):
    """
    Split profile flag byte into

    - amount of additional bytes of extended information
    - event byte presence, which is zero or one

    """
    return value & 0x7f, value >> 7


