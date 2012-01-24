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
OSTC dive computer binary data parsing routines.
"""

import logging
import re
from collections import namedtuple
from struct import unpack, calcsize
from binascii import hexlify

log = logging.getLogger('kenozooid.driver.ostc')

# command 'a' output
Data = namedtuple('Data', 'preamble eeprom voltage ver1 ver2 profiles')
FMT_STATUS = '<6s256sHbb'
LEN_STATUS = calcsize(FMT_STATUS)

# EEPROM data, command 'g' output (nfy)
EEPROMData = namedtuple('EEPROMData', 'serial dives data')
FMT_EEPROM = '<HH252s'

# profile data is one of
# - FAFA20..(42)..FBFB...FDFD
# - FAFA21..(52)..FBFB...FDFD
RE_PROFILES = re.compile(b'(\xfa\xfa' \
        b'(\x20.{42}|\x21.{52})\xfb\xfb)' \
        b'(.+?\xfd\xfd)', re.DOTALL)

# dive profile header
DiveHeader = namedtuple('DiveHeader', """\
version month day year hour minute max_depth dive_time_m dive_time_s
min_temp surface_pressure desaturation
gas1_o2 gas1_he gas2_o2 gas2_he gas3_o2 gas3_he gas4_o2 gas4_he gas5_o2 gas5_he
gas6_o2 gas6_he gas
ver1 ver2 voltage sampling div_temp div_deco div_gf div_ppo2
div_deco_debug div_cns salnity max_cns
""")
FMT_DIVE_HEADER = '<6BHHB' 'HHH' '10B' 'BBB' 'BBHB4B' 'BBBB'

DiveHeader_191 = namedtuple('DiveHeader_191',
        DiveHeader._fields + ('avg_depth', 'dive_time_total_s',
            'gf_lo', 'gf_hi', 'deco_type',
            'reserved1', 'reserved2', 'reserved3'))
FMT_DIVE_HEADER_191 = FMT_DIVE_HEADER + 'HH' 'BB' 'BBBB'

# dive profile data block sample
DiveSample = namedtuple('DiveSample', 'depth alarm gas_set_o2 gas_set_he'
    ' current_gas setpoint temp deco_depth deco_time gf ppo2 cns')


def get_data(data):
    """
    Get status information and profile raw data, see `Data` named tuple.
    """
    dump = Data(*unpack(FMT_STATUS, data[:LEN_STATUS]),
            profiles=data[LEN_STATUS:])
    eeprom = EEPROMData(*unpack(FMT_EEPROM, dump.eeprom))
    dump = dump._replace(eeprom=eeprom)
    log.debug('unpacked status dump, voltage {}, version {}.{}, serial {}' \
        .format(dump.voltage, dump.ver1, dump.ver2, dump.eeprom.serial))
    return dump


def profiles(data):
    """
    Split profile data into individual dive profiles using profile
    regular expression `RE_PROFILES`.

    Collection of tuples (header, block) is returned

     header
        dive profile header 
     block 
        dive profile block data

    """
    return ((h, p) for h, _, p in RE_PROFILES.findall(data))


def header(data):
    """
    Parse OSTC dive profile header, see `DiveHeader` named tuple.
    """
    if len(data) == 47:
        header = DiveHeader(*unpack(FMT_DIVE_HEADER, data[2:-2]))
    elif len(data) == 57:
        header = DiveHeader_191(*unpack(FMT_DIVE_HEADER_191, data[2:-2]))
    else:
        raise ValueError('Unknown length of profile header: {}'.format(len(data)))

    log.debug('parsed dive header {0.year:>02d}-{0.month:>02d}-{0.day:>02d}' \
        ' {0.hour:>02d}:{0.minute:>02d}' \
        ' max depth={0.max_depth}'.format(header))
    return header


def dive_data(header, data):
    """
    Parse OSTC dive profile data block.
    """
    div_temp_s, div_temp_c = divisor(header.div_temp)
    div_deco_s, div_deco_c = divisor(header.div_deco)
    div_gf_s, div_gf_c = divisor(header.div_gf)
    div_ppo2_s, div_ppo2_c = divisor(header.div_ppo2)
    div_deco_debug_s, div_deco_debug_c = divisor(header.div_deco_debug)
    div_cns_s, div_cns_c = divisor(header.div_cns)

    log.debug('header divisor values {:x} {:x} {:x} {:x} {:x} {:x}'
        .format(header.div_temp, header.div_deco, header.div_gf,
            header.div_ppo2, header.div_deco_debug, header.div_cns))

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
        log.debug('sample {} info: depth = {:.2f}, pfb = {:x}, size = {}, ' \
            'data: {}'.format(j, depth, pfb, size, hexlify(data[i:i + size])))

        alarm = None
        gas_set = 0
        gas_set_o2 = None
        gas_set_he = None
        gas_change = 0
        current_gas = None
        setpoint_change = 0
        setpoint = None
        # parse event byte information
        if event:
            v = data[i]
            i += 1
            alarm = v & 0x0f
            gas_set = v & 0x10
            gas_change = v & 0x20
            setpoint_change = v & 0x40

            log.debug('alarm = {}, gas_set = {}, gas_change = {},' \
                ' setpoint_change = {}'.format(alarm, gas_set, gas_change,
                    setpoint_change))

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
            log.debug('deco time {}, depth {}'.format(deco_time, deco_depth))
        else:
            deco_depth, deco_time = None, None

        gf = sample_data(data, i, j, div_gf_s, div_gf_c)
        if gf is not None:
            i += div_gf_c
            div_bytes += div_gf_c

        ppo2 = sample_data(data, i, j, div_ppo2_s, div_ppo2_c)
        if ppo2 is not None:
            i += div_ppo2_c
            div_bytes += div_ppo2_c
            log.debug('ppo2 {}'.format(hexlify(ppo2)))

        deco_debug = sample_data(data, i, j, div_deco_debug_s, div_deco_debug_c)
        if deco_debug is not None:
            i += div_deco_debug_c
            div_bytes += div_deco_debug_c
            log.debug('deco debug {}'.format(hexlify(deco_debug)))

        cns = sample_data(data, i, j, div_cns_s, div_cns_c)
        if cns is not None:
            i += div_cns_c
            div_bytes += div_cns_c
            log.debug('cns {}'.format(hexlify(cns)))

        if setpoint_change:
            setpoint = data[i]
            i += 1
            setpoint_change = 1
            log.debug('setpoint change {}'.format(setpoint))
            
        if size != event + gas_set + gas_change + setpoint_change + div_bytes:
            log.debug('invalid dive data, sample = {}, depth = {:.2f},' \
                ' pfb = {:x}, size = {}, event = {}, alarm = {}, temp = {},' \
                ' gas_set = {}, gas_change = {}, cns = {},' \
                ' setpoint_change = {}, setpoint = {},' 
                ' div_bytes = {}, deco_debug = {}'
                .format(j, depth, pfb, size, event, alarm, temp, gas_set,
                            gas_change, cns, setpoint_change, setpoint,
                            div_bytes,
                            hexlify(deco_debug) if deco_depth else []))
            raise ValueError('Invalid dive')

        # is a sample within dive total time? if not, then skip sample
        if header.sampling * (j - 1) <= dive_total_time:
            yield DiveSample(depth, alarm, gas_set_o2, gas_set_he, current_gas,
                    setpoint, temp, deco_depth, deco_time, gf, ppo2, cns)
        else:
            log.debug('skipped sample {} (out of dive time), seek {}'
                .format(j, i))
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
        Sample item data bytes count.
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


# vim: sw=4:et:ai
