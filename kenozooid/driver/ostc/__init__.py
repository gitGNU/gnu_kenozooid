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
Driver for OSTC, an open source dive computer.

OSTC dive computer specification and documentation of communication
protocol can be found at address

    http://www.heinrichsweikamp.net/

"""

from datetime import datetime, timedelta
from serial import Serial, SerialException
from binascii import hexlify
from functools import partial
from operator import attrgetter
import logging

log = logging.getLogger('kenozooid.driver.ostc')

import kenozooid.uddf as ku
import kenozooid.component as kc
from kenozooid.driver import DeviceDriver, Simulator, DataParser, DeviceError
from kenozooid.units import C2K, B2Pa
from . import parser as ostc_parser
import kenozooid.data as kd

GAS_GETTERS = dict(
    zip(range(1, 7), (attrgetter('gas{}_o2'.format(i), 'gas{}_he'.format(i))
        for i in range(1, 7))))

def pressure(depth):
    """
    Convert depth in meters to pressure in mBars.
    """
    return int(depth + 10)


@kc.inject(DeviceDriver, id='ostc', name='OSTC Driver',
        models=('OSTC', 'OSTC Mk.2', 'OSTC 2N'))
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
        log.debug('sending command {}'.format(cmd))
        self._device.write(cmd)
        log.debug('returned after command {}'.format(cmd))


    def _read(self, size):
        assert size > 0
        log.debug('reading {} byte(s)'.format(size))
        data = self._device.read(size)
        log.debug('got {} byte(s) of data'.format(len(data)))
        if len(data) != size:
            raise DeviceError('Device communication error')
        return data


    @staticmethod
    def scan(port=None):
        """
        Look for OSTC dive computer connected to one of USB ports.

        Library pySerial is used, therefore no scanning and port shall be
        specified.
        """
        try:
            drv = OSTCDriver(port)
            log.debug('connected ostc to port {}'.format(port))
            yield drv
        except SerialException as ex:
            log.debug('{}'.format(ex))


    def version(self):
        """
        Read OSTC dive computer firmware version.
        """
        self._write(b'e')
        v1, v2 = self._read(2)
        self._read(16) # fingerprint, ignore as it can be 0x00 if not built yet
        return 'OSTC {}.{}'.format(v1, v2)



@kc.inject(Simulator, id='ostc')
class OSTCSimulator(object):
    """
    OSTC dive computer simulator support.
    """
    def start(self):
        """
        Put OSTC dive computer into dive simulation mode. The dive computer
        will not show dive mode screen until "dived" into configured depth
        (option CF0).
        """
        self.driver._write(b'c')


    def stop(self):
        """
        Stop OSTC dive simulation mode. OSTC stays in dive mode until
        appropriate period of time passes, which is configured with option
        CF2.
        """
        self.driver._write(b'\x00')


    def depth(self, depth):
        """
        Send dive computer to given depth.
        """
        p = pressure(round(depth))
        self.driver._write(bytearray((p,)))



@kc.inject(DataParser, id='ostc', data=('gas',))
class OSTCDataParser(object):
    """
    OSTC dive computer data parser.
    """
    def dump(self):
        """
        Download OSTC status and all dive profiles.
        """
        self.driver._write(b'a')
        data = self.driver._read(33034)
        status = ostc_parser.get_data(data)
        if (status.ver1, status.ver2) >= (1, 91):
            log.debug('detected ostc firmware >= 1.91, reading additional data')
            data += self.driver._read(32768)
        return data


    def dives(self, dump):
        """
        Convert dive data into UDDF format.
        """
        ostc_data = ostc_parser.get_data(dump.data)

        for h, p in ostc_parser.profiles(ostc_data.profiles):
            log.debug('header: {}'.format(hexlify(h)))
            log.debug('profile: {}'.format(hexlify(p)))

            header = ostc_parser.header(h)
            dive_data = ostc_parser.dive_data(header, p)

            # set time of the start of dive
            st = datetime(2000 + header.year, header.month, header.day,
                    header.hour, header.minute)
            # ostc dive computer saves time at the end of dive in its
            # memory, so substract the dive time;
            # sampling amount is substracted as well as below (0, 0)
            # waypoint is added
            duration = timedelta(minutes=header.dive_time_m,
                    seconds=header.dive_time_s + header.sampling)
            st -= duration

            # firmware ver < 1.91 has no average depth information
            avg_depth = header.avg_depth / 100.0 \
                    if hasattr(header, 'avg_depth') else None

            try:
                profile = list(self._get_profile(header, dive_data))
                yield kd.Dive(datetime=st,
                    depth=header.max_depth / 100.0,
                    duration=duration.seconds,
                    temp=C2K(header.min_temp / 10.0),
                    avg_depth=avg_depth,
                    profile=profile)
            except ValueError as ex:
                log.error('invalid dive {0.year:>02d}-{0.month:>02d}-{0.day:>02d}' \
                    ' {0.hour:>02d}:{0.minute:>02d}' \
                    ' max depth={0.max_depth}'.format(header))


    def _get_profile(self, header, dive_data):
        """
        Parse OSTC dive samples.
        """
        # ostc starts dive below at a depth, so add (0, 0) sample
        yield kd.Sample(depth=0.0, time=0, gas=self._get_gas(header, header.gas))

        for i, sample in enumerate(dive_data, 1):
            temp = C2K(sample.temp) if sample.temp else None

            setpoint = B2Pa(sample.setpoint / 100.0) if sample.setpoint else None

            # deco info
            deco_time = sample.deco_time * 60.0 if sample.deco_depth else None
            deco_depth = sample.deco_depth if sample.deco_depth else None
            deco_alarm = False
            if sample.alarm is not None:
                deco_alarm = sample.alarm in (2, 3)

            gas = None
            if sample.current_gas is not None:
                gas = self._get_gas(header, sample.current_gas)
            elif sample.gas_set_o2 is not None:
                gas = kd.gas(sample.gas_set_o2, sample.gas_set_he)

            yield kd.Sample(depth=sample.depth,
                    time=(i * header.sampling),
                    alarm=('deco',) if deco_alarm else None,
                    temp=temp,
                    setpoint=setpoint,
                    setpointby='user' if setpoint else None,
                    deco_time=deco_time,
                    deco_depth=deco_depth,
                    gas=gas)

        yield kd.Sample(depth=0.0, time=(i + 1) * header.sampling)


    def _get_gas(self, header, gas_no):
        """
        Get gas information from OSTC dive header.

        :Parameters:
         header
            Dive header information.
         gas_no
            Gas number to get (1-6).
        """
        o2, he = GAS_GETTERS[gas_no](header)
        return kd.gas(o2=o2, he=he)


    def version(self, data):
        """
        Get OSTC model and version information from raw data.
        """
        status = ostc_parser.get_data(data)
        model = 'OSTC'
        if status.eeprom.serial > 2047:
            model = 'OSTC 2N'
        elif status.eeprom.serial > 300:
            model = 'OSTC Mk.2'
        return '{} {}.{:02}'.format(model, status.ver1, status.ver2)


# vim: sw=4:et:ai
