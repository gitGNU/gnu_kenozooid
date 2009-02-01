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

from serial import Serial, SerialException
import array

from kenozooid.iface import DeviceDriver, Simulator, inject

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
    return depth + 10


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
                timeout=3)

    def _write(self, cmd):
        self._device.write(cmd)

    def _read(self, size):
        assert size > 0
        return self._device.read(size)


    @staticmethod
    def scan():
        """
        Look for OSTC dive computer connected to one of USB serial ports.
        """
        for i in range(10):
            port = '/dev/ttyUSB%d' % i
            print 'trying port', port
            try:
                drv = OSTCDriver(port)
                yield drv
            except SerialException, ex:
                print 'port %s failed: %s' % (port, ex)


    def version(self):
        """
        Read OSTC dive computer firmware version and firmware fingerprint.
        """
        print 'write'
        self._write('e')
        print 'returned'
        data = self._read(2)
        v1, v2 = tuple(map(ord, data))
        print 'read done almost'
        data = self._read(16)
        fingerprint = ''.join('%x' % ord(c) for c in data)
        return 'OSTC %s.%s (fingerprint %s)' % (v1, v2, fingerprint.upper())



@inject(Simulator, id='ostc')
class OSTCSimulator(object):
    def __init__(self, driver):
        super(OSTCSimulator, self).__init__()
        self._driver = driver

    def start(self):
        print 'starting'
        self._driver._write('c')
        print 'started'

    def stop(self):
        self._driver._write(byte(0))

    def depth(self, depth):
        pressure = depth + 10
        self._driver._write(byte(pressure))

