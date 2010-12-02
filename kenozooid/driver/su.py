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
from functools import partial
from Queue import Queue, Full, Empty
from threading import Thread
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
        return 'Sensus Ultra %d.%d' % (dump.ver2, dump.ver1)



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

        parser = ct.c_void_p()
        rc = lib.reefnet_sensusultra_parser_create(ct.byref(parser))
        if rc != 0:
            raise DeviceError('Cannot create data parser')
        
        hd = dump.data.read(SIZE_MEM_HANDSHAKE)
        hdp = HandshakeDump._make(unpack(FMT_HANDSHAKE, hd[:8]))

        ud = dump.data.read(SIZE_MEM_USER)

        dd = ct.create_string_buffer('\000' * SIZE_MEM_DATA)
        dd.raw = dump.data.read(SIZE_MEM_DATA)

        # boot time = host time - device time (sensus time)
        btime = time.mktime(dump.time.timetuple()) - hdp.time

        dq = Queue(5)
        parse_dive = partial(self.parse_dive,
                parser=parser, boot_time=btime, dives=dq)
        extract_dives = partial(lib.reefnet_sensusultra_extract_dives,
                None, dd, SIZE_MEM_DATA, FuncDive(parse_dive), ct.py_object(None))

        # http://bugs.python.org/issue1395552
        def run(self):
            self.result = extract_dives()
        Thread.run = run
        t = Thread()
        #t = Thread(target=extract_dives)

        t.start()
        while t.is_alive():
            try:
                dn = dq.get(False)
            except Empty:
                time.sleep(0.1)
            else:
                yield dn

        # there still can be some dive nodes left in the queue
        while not dq.empty():
            yield dq.get()

        if t.result == 0:
            raise StopIteration()
        else:
            raise DeviceError('Failed to extract dives properly')

    
    def parse_dive(self, buffer, size, pdata, parser, boot_time, dives):
        """
        Callback used by libdivecomputer's library function to extract
        dives from a device and put it into dives queue.

        :Parameters:
         buffer
            Buffer with binary dive data.
         size
            Size of buffer dive data.
         pdata
            Parser user data (nothing at the moment).
         boot_time
            Sensus Ultra boot time.
         dives
            Queue of dives to be consumed by caller.
        """
        log.debug('parsing dive')

        lib = ct.CDLL('libdivecomputer.so.0')
        lib.parser_set_data(parser, buffer, size)

        # dive time is in seconds since boot time 
        dive_time = unpack('<L', buffer[4:8])[0]
        log.debug('got divetime: {0}'.format(dive_time))
        st = datetime.fromtimestamp(boot_time + dive_time)

        dn = ku.create_dive_data(time=st)

        parse_sample = partial(self.parse_sample,
                dive_node=dn,
                sdata={})
        lib.parser_samples_foreach(parser,
                FuncSample(parse_sample),
                ct.py_object(None))

        try:
            dives.put(dn, timeout=30)
        except Full:
            log.error('could not parse dives due to internal queue timeout')
            return 0

        return 1


    def parse_sample(self, st, sample, pdata, dive_node, sdata):
        """
        Convert sample data generated with libdivecomputer library into
        UDDF waypoint structure.

        :Parameters:
         st
            Sample type as specified in parser.h.
         sample
            Sample data.
         pdata
            Parser user data (nothing at the moment).
         dive_node
            UDDF dive node to which to be created sample belongs.
         sdata
            Temporary sample data.
        """
        # depth is the last sample type generated by libdivecomputer,
        # create the waypoint then
        if st == SampleType.time:
            sdata['time'] = sample.time
        elif st == SampleType.temperature:
            sdata['temp'] = C2K(sample.temperature)
        elif st == SampleType.depth:
            sdata['depth'] = sample.depth

            ku.create_dive_profile_sample(dive_node, self.UDDF_SAMPLE, **sdata)
            sdata.clear() # clear temporary data
        else:
            log.warn('unknown sample type', st)
        return 1


# vim: sw=4:et:ai
