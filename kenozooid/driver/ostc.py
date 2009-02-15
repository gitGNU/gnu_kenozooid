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
Support for OSTC, an open source dive computer.

OSTC dive computer specification and documentation of communication
protocol can be found at address

    http://www.heinrichsweikamp.net/ostc/en/

"""

from serial import Serial, SerialException
import array
import logging
import math

log = logging.getLogger('kenozooid.driver.ostc')

from kenozooid.component import inject
from kenozooid.driver import DeviceDriver, Simulator, MemoryDump, DeviceError

def byte(i):
    """
    Convert integer to a byte.
    """
    b = array.array('B', [i])
    return b.tostring()


def pressure(depth):
    """
    Convert depth in meters to pressure in mBars.
    """
    return int(depth + 10)


@inject(DeviceDriver, id='ostc', name='OSTC Driver')
class OSTCDriver(object):
    """
    OSTC dive computer driver.
    """
    def __init__(self, port):
        super(OSTCDriver, self).__init__()

        self._device = Serial(port=port,
                baudrate=115200,
                bytesize=8,
                stopbits=1,
                parity='N',
                timeout=5) # 1s timeout is too short sometimes with 'a' command

    def _write(self, cmd):
        log.debug('sending command %s' % cmd)
        self._device.write(cmd)
        log.debug('returned after command %s' % cmd)


    def _read(self, size):
        assert size > 0
        log.debug('reading %d byte(s)' % size)
        data = self._device.read(size)
        log.debug('got %d byte(s) of data' % len(data))
        if len(data) != size:
            raise DeviceError('Device communication error')
        return data


    @staticmethod
    def scan():
        """
        Look for OSTC dive computer connected to one of USB serial ports.
        """
        for i in range(10):
            port = '/dev/ttyUSB%d' % i
            log.debug('trying port %s' % port)
            try:
                drv = OSTCDriver(port)
                log.debug('found port %s' % port)
                yield drv
            except SerialException, ex:
                log.debug('%s' % ex)


    def version(self):
        """
        Read OSTC dive computer firmware version and firmware fingerprint.
        """
        self._write('e')
        data = self._read(2)
        v1, v2 = tuple(map(ord, data))
        data = self._read(16)
        fingerprint = ''.join('%x' % ord(c) for c in data)
        return 'OSTC %s.%s (fingerprint %s)' % (v1, v2, fingerprint.upper())



@inject(Simulator, id='ostc')
class OSTCSimulator(object):
    def start(self):
        self.driver._write('c')

    def stop(self):
        self.driver._write(byte(0))

    def depth(self, depth):
        p = pressure(depth)
        self.driver._write(byte(p))


@inject(MemoryDump, id='ostc')
class OSTCMemoryDump(object):
    """
    OSTC dive computer memory dump.
    """
    def dump(self):
        """
        Download OSTC status and all dive profiles.
        """
        self.driver._write('a')
        return self.driver._read(33034)


    def convert(self, data, tree):
        """
        Convert dive profiles to UDDF format.
        """
        root = tree.getroot()

