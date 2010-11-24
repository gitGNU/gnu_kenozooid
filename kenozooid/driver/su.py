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

It uses libdivecomputer library from

    http://divesoftware.org/libdc/
"""

import ctypes as ct
from datetime import datetime
from dateutil.parser import parse as dparse
from struct import unpack, pack
from collections import namedtuple
from lxml import etree as et
import time

import logging
log = logging.getLogger('kenozooid.driver.su')

import kenozooid.uddf as ku
import kenozooid.component as kc
from kenozooid.driver import DeviceDriver, MemoryDump, DeviceError
from kenozooid.units import C2K

SIZE_MEM_USER = 16384
SIZE_MEM_DATA = 2080768
SIZE_MEM_HANDSHAKE = 24
SIZE_MEM_SENSE = 6

# Reefnet Sensus Ultra handshake packet (only versiona and serial supported
# at the moment)
FMT_HANDSHAKE = '<bbHL'
HandshakeDump = namedtuple('HandshakeDump', 'ver1 ver2 serial time')

#
# libdivecomputer data structures and constants
#

# see parser.h:parser_sample_type_t
SampleType = namedtuple('SampleType', 'time depth pressure temperature' \
    ' event rbt heartbeat bearing vendor')._make(range(9))


class Pressure(ct.Structure):
    _fields_ = [
        ('tank', ct.c_int),
        ('value', ct.c_double),
    ]


class Event(ct.Structure):
    _fields_ = [
        ('type', ct.c_int),
        ('time', ct.c_int),
        ('flags', ct.c_int),
        ('value', ct.c_int),
    ]


class Vendor(ct.Structure):
    _fields_ = [
        ('type', ct.c_int),
        ('size', ct.c_int),
        ('data', ct.c_void_p), 
    ]


class SampleValue(ct.Union):
    _fields_ = [
        ('time', ct.c_int),
        ('depth', ct.c_double),
        ('pressure', Pressure),
        ('temperature', ct.c_double),
        ('event', Event),
        ('rbt', ct.c_int),
        ('heartbeat', ct.c_int),
        ('bearing', ct.c_int),
        ('vendor', Vendor),
    ]


# dive and sample data callbacks 
FuncDive = ct.CFUNCTYPE(ct.c_int, ct.POINTER(ct.c_char), ct.c_int, ct.py_object)
FuncSample = ct.CFUNCTYPE(ct.c_int, ct.c_int, SampleValue, ct.py_object)


@kc.inject(DeviceDriver, id='su', name='Sensus Ultra Driver',
        models=('Sensus Ultra',))
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
        rc = 0
        if port is not None:
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

        # take 8 bytes for now (version, serial and time)
        dump = HandshakeDump._make(unpack(FMT_HANDSHAKE, hd.raw[:8]))
        return 'Sensus Ultra %d.%d (serial %d)' % (dump.ver2, dump.ver1, dump.serial)



@kc.inject(MemoryDump, id='su')
class SensusUltraMemoryDump(object):
    """
    Reefnet Sensus Ultra dive logger memory dump.
    """
    UDDF_SAMPLE = {
        'depth': 'uddf:depth',
        'time': 'uddf:divetime',
        'temp': 'uddf:temperature',
    }
    def dump(self):
        """
        Download Sensus Ultra

        - handshake packet
        - user data 
        - data of all dive profiles
        """
        dev = self.driver.dev
        lib = self.driver.lib

        hd = ct.create_string_buffer('\000' * SIZE_MEM_HANDSHAKE)
        ud = ct.create_string_buffer('\000' * SIZE_MEM_USER)
        dd = ct.create_string_buffer('\000' * SIZE_MEM_DATA)

        rc = lib.reefnet_sensusultra_device_read_user(dev, ud, SIZE_MEM_USER)
        if rc != 0:
            raise DeviceError('Device communication error')

        rc = lib.reefnet_sensusultra_device_get_handshake(dev, hd, SIZE_MEM_HANDSHAKE)
        if rc != 0:
            raise DeviceError('Device communication error')

        rc = lib.device_dump(dev, dd, SIZE_MEM_DATA)
        if rc != 0:
            raise DeviceError('Device communication error')

        return hd.raw[:-1] + ud.raw[:-1] + dd.raw[:-1]


    def convert(self, dump):
        """
        Convert Reefnet Sensus Ultra dive profiles data into UDDF format
        dive nodes.
        """
        #dev = self.driver.dev
        #lib = self.driver.lib
        lib = ct.CDLL('libdivecomputer.so.0')

        parser = self.parser = ct.c_void_p()
        rc = lib.reefnet_sensusultra_parser_create(ct.byref(parser))
        if rc != 0:
            raise DeviceError('Cannot create data parser')
        
        hd = dump.data.read(SIZE_MEM_HANDSHAKE)
        hdp = HandshakeDump._make(unpack(FMT_HANDSHAKE, hd[:8]))

        ud = dump.data.read(SIZE_MEM_USER)

        dd = ct.create_string_buffer('\000' * SIZE_MEM_DATA)
        dd.raw = dump.data.read(SIZE_MEM_DATA)

        data = {
            'dtime': time.mktime(dump.time.timetuple()), # download time
            'stime': hdp.time,                           # sensus time at download time
        }

        self.dives = []
        rc = lib.reefnet_sensusultra_extract_dives(None,
                dd,
                SIZE_MEM_DATA,
                FuncDive(self.parse_dive),
                ct.py_object(data))
        if rc != 0:
            raise DeviceError('Cannot extract dives')
        return self.dives

    
    def parse_dive(self, buffer, size, data):
        """
        Callback used by libdivecomputer's library function to extract
        dives from a device.

        :Parameters:
         buffer
            Buffer with binary dive data.
         size
            Size of buffer dive data.
         data
            User data (UTC download time, Sensus Ultra download time).
        """
        lib = ct.CDLL('libdivecomputer.so.0')
        parser = self.parser

        # get dive time
        dive_time = unpack('<L', buffer[4:8])[0]
        st = datetime.fromtimestamp(data['dtime'] + dive_time - data['stime'])

        self.dive_node, dt = ku.create_node('uddf:dive/uddf:datetime')
        dt.text = st.strftime(ku.FMT_DATETIME)

        lib.parser_set_data(parser, buffer, size)
        lib.parser_samples_foreach(parser,
                FuncSample(self.parse_sample),
                ct.py_object({'time': None, 'depth': None, 'temp': None}))

        self.dives.append(self.dive_node)

        return 1


    def parse_sample(self, st, sample, data):
        """
        Convert sample data generated with libdivecomputer library into
        UDDF waypoint structure.

        :Parameters:
         st
            Sample type as specified in parser.h.
         sample
            Sample data.
         data
            User data (current time, depth and temperature).
        """
        # depth is the last sample type generated by libdivecomputer,
        # create the waypoint then
        if st == SampleType.time:
            data['time'] = sample.time
        elif st == SampleType.temperature:
            data['temp'] = sample.temperature
        elif st == SampleType.depth:
            data['depth'] = round(sample.depth, 2)

            ku.create_dive_profile_sample(self.dive_node, self.UDDF_SAMPLE, **data)

            # clear cached data
            data['depth'] = None
            data['time'] = None
            data['temp'] = None
        else:
            log.warn('unknown sample type', st)
        return 1



