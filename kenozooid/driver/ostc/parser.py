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
from struct import unpack

log = logging.getLogger('kenozooid.driver.ostc')

# command 'a' output
StatusDump = namedtuple('StatusDump', 'preamble eeprom voltage ver1 ver2 profile')
FMT_STATUS = '<6s256sHbb32768s'

# profile data is FA0FA..(43)..FBFB...FDFD
RE_PROFILE = re.compile('(\xfa\xfa.{43}\xfb\xfb)(.+?\xfd\xfd)', re.DOTALL)

# dive profile header
DiveHeader = namedtuple('DiveHeader', """\
start version month day year hour minute max_depth dive_time_m dive_time_s
min_temp surface_pressure desaturation gas1 gas2 gas3 gas4 gas5 gas6 gas
ver1 ver2 voltage sampling div_temp div_deco div_tank div_ppo2
div_res1 div_res2 spare end
""")
FMT_DIVE_HEADER = '<H6BHHB' 'HHH6HB' 'BBHB4B' 'BBHH'


def status(data):
    """
    Split status and profile data, see `StatusDump` named tuple.
    """
    dump = StatusDump._make(unpack(FMT_STATUS, data))
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
    Parse OSTC header and data block of a dive profile, see `DiveHeader`
    named tuple.
    """
    header = DiveHeader._make(unpack(FMT_DIVE_HEADER, data))
    log.debug('parsed dive header {0.year:>02d}/{0.month:>02d}/{0.day:>02d},' \
        ' max depth {0.max_depth}'.format(header))
    return header


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


