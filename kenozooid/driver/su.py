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
Driver for Reefnet Sensus Ultra dive logger.
"""

import ctypes as ct
from struct import unpack
from collections import namedtuple
import logging
from kenozooid.component import inject

log = logging.getLogger('kenozooid.driver.su')

from kenozooid.driver import DeviceDriver, MemoryDump, DeviceError

SIZE_MEM_USER = 16384
SIZE_MEM_DATA = 2080768
SIZE_MEM_HANDSHAKE = 24
SIZE_MEM_SENSE = 6

# handshake data
FMT_HANDSHAKE = '<bbH'
HandshakeDump = namedtuple('HandshakeDump', 'ver1 ver2 serial')

@inject(DeviceDriver, id='su', name='Sensus Ultra Driver')
class SensusUltraDriver(object):
    """
    Sensus Ultra dive logger driver.
    """
    def __init__(self, dev, lib):
        self.dev = dev
        self.lib = lib


    @staticmethod
    def scan(port=None):
        """
        Look for Reefnet Sensus Ultra dive logger connected to one of USB
        ports.

        Library `libdivecomputer` is used, therefore no scanning and port
        shall be specified.
        """
        lib = ct.CDLL('libdivecomputer.so.0')

        dev = ct.c_void_p()
        rc = lib.reefnet_sensusultra_device_open(ct.byref(dev), port)
        if rc == 0:
            drv = SensusUltraDriver(dev, lib)
            log.debug('found Reefnet Sensus Ultra driver using' \
                    ' libdivecomputer library on port %s' % port)
            yield drv


    def version(self):
        """
        Read Reefnet Sensus Ultra version and serial number.
        """

        sd = ct.create_string_buffer('\000' * SIZE_MEM_SENSE)
        rc = self.lib.reefnet_sensusultra_device_sense(self.dev, sd, SIZE_MEM_SENSE)
        if rc != 0:
            raise DeviceError('Device communication error')

        hd = ct.create_string_buffer('\000' * SIZE_MEM_HANDSHAKE)
        rc = self.lib.reefnet_sensusultra_device_get_handshake(self.dev, hd, SIZE_MEM_HANDSHAKE)
        if rc != 0:
            raise DeviceError('Device communication error')

        # take 4 bytes for now (version and serial)
        dump = HandshakeDump._make(unpack(FMT_HANDSHAKE, hd.raw[:4]))
        return 'Sensus Ultra %d.%d (serial %d)' % (dump.ver2, dump.ver1, dump.serial)



@inject(MemoryDump, id='su')
class SensusUltraMemoryDump(object):
    """
    Reefnet Sensus Ultra dive logger memory dump.
    """
    def dump(self):
        """
        Download Sensus Ultra user configuration and all dive profiles.
        """
        dev = self.driver.dev
        lib = self.driver.lib

        ud = ct.create_string_buffer('\000' * SIZE_MEM_USER)
        dd = ct.create_string_buffer('\000' * SIZE_MEM_DATA)

        rc = lib.reefnet_sensusultra_device_read_user(dev, ud, SIZE_MEM_USER)
        if rc != 0:
            raise DeviceError('Device communication error')

        rc = lib.device_dump(dev, dd, SIZE_MEM_DATA)
        if rc != 0:
            raise DeviceError('Device communication error')

        return ud.raw[:-1] + dd.raw[:-1]


    def convert(self, data, tree):
        """
        Convert dive profiles to UDDF format.
        """
