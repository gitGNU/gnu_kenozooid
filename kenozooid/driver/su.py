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
Driver for Reefnet Sensus Ultra dive logger.

It uses libdivecomputer library from

    http://divesoftware.org/libdc/
"""

import ctypes as ct
from collections import OrderedDict
from datetime import datetime
from dateutil.parser import parse as dparse
from struct import unpack, pack
from collections import namedtuple
from lxml import etree as et
from functools import partial
from queue import Queue, Full, Empty
from concurrent.futures import ThreadPoolExecutor
import time
import operator

import logging
log = logging.getLogger('kenozooid.driver.su')

import kenozooid.uddf as ku
import kenozooid.data as kd
import kenozooid.component as kc
from kenozooid.driver import DeviceDriver, DataParser, DeviceError
from kenozooid.units import C2K

SIZE_MEM_USER = 16384
SIZE_MEM_DATA = 2080768
SIZE_MEM_HANDSHAKE = 24
SIZE_MEM_SENSE = 6

START_HANDSHAKE = 0
END_HANDSHAKE = START_USER = SIZE_MEM_HANDSHAKE
END_USER = START_DATA = START_USER + SIZE_MEM_USER
END_DATA = START_DATA + SIZE_MEM_DATA

# Reefnet Sensus Ultra handshake packet (only version and serial supported
# at the moment)
HandshakeDump = namedtuple('HandshakeDump', 'ver1 ver2 serial time')
FMT_HANDSHAKE = '<bbHL'

DiveHeader = namedtuple('DiveHeader', 'time interval threshold' 
    ' endcount averaging')
# 4 bytes of padding, it is start of the header (0x00000000)
FMT_DIVE_HEADER = '<4xL4H'

#
# libdivecomputer data structures and constants
#

# see buffer.c, buffer.h
class DCBuffer(ct.Structure):
    _fields_ = [
        ('data', ct.POINTER(ct.c_char)),
        ('capacity', ct.c_size_t),
        ('offset', ct.c_size_t),
        ('size', ct.c_size_t),
    ]

# see parser.h:parser_sample_type_t
SampleType = namedtuple('SampleType', 'time depth pressure temperature' \
    ' event rbt heartbeat bearing vendor')._make(range(9))


class Pressure(ct.Structure):
    _fields_ = [
        ('tank', ct.c_uint),
        ('value', ct.c_double),
    ]


class Event(ct.Structure):
    _fields_ = [
        ('type', ct.c_uint),
        ('time', ct.c_uint),
        ('flags', ct.c_uint),
        ('value', ct.c_uint),
    ]


class Vendor(ct.Structure):
    _fields_ = [
        ('type', ct.c_uint),
        ('size', ct.c_uint),
        # fixme: (segv): ('data', ct.c_void_p),
    ]


class SampleValue(ct.Union):
    _fields_ = [
        ('time', ct.c_uint),
        ('depth', ct.c_double),
        ('pressure', Pressure),
        ('temperature', ct.c_double),
        ('event', Event),
        ('rbt', ct.c_uint),
        ('heartbeat', ct.c_uint),
        ('bearing', ct.c_uint),
        ('vendor', Vendor),
    ]


# dive and sample data callbacks 
FuncDive = ct.CFUNCTYPE(ct.c_uint, ct.POINTER(ct.c_char), ct.c_uint,
    ct.POINTER(ct.c_char), ct.c_uint, ct.c_void_p)
FuncSample = ct.CFUNCTYPE(None, ct.c_int, SampleValue, ct.c_void_p)


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
            rc = lib.reefnet_sensusultra_device_open(ct.byref(dev),
                    port.encode())
        if rc == 0:
            drv = SensusUltraDriver(dev, lib)
            log.debug('found Reefnet Sensus Ultra driver using' \
                    ' libdivecomputer library on port {}'.format(port))
            yield drv
        else:
            log.debug('libdc error: {}'.format(rc))


    def version(self):
        """
        Read Reefnet Sensus Ultra version and serial number.
        """

        sd = ct.create_string_buffer(SIZE_MEM_SENSE)
        rc = self.lib.reefnet_sensusultra_device_sense(self.dev, sd, SIZE_MEM_SENSE)
        if rc != 0:
            raise DeviceError('Device communication error')

        hd = ct.create_string_buffer(SIZE_MEM_HANDSHAKE)
        rc = self.lib.reefnet_sensusultra_device_get_handshake(self.dev, hd, SIZE_MEM_HANDSHAKE)
        if rc != 0:
            raise DeviceError('Device communication error')

        # take 8 bytes for now (version, serial and time)
        dump = _handshake(hd.raw)
        return 'Sensus Ultra %d.%d' % (dump.ver2, dump.ver1)



@kc.inject(DataParser, id='su', data=())
class SensusUltraDataParser(object):
    """
    Reefnet Sensus Ultra dive logger data parser.
    """

    def dump(self):
        """
        Download Sensus Ultra

        - handshake packet
        - user data 
        - data of all dive profiles
        """
        dev = self.driver.dev
        lib = self.driver.lib

        hd = ct.create_string_buffer(SIZE_MEM_HANDSHAKE)
        ud = ct.create_string_buffer(SIZE_MEM_USER)
        dd = ct.cast(lib.dc_buffer_new(SIZE_MEM_DATA), ct.POINTER(DCBuffer))

        log.debug('loading user data')
        rc = lib.reefnet_sensusultra_device_read_user(dev, ud, SIZE_MEM_USER)
        if rc != 0:
            log.debug('read error rc = {}'.format(rc))
            raise DeviceError('Device communication error')

        log.debug('loading handshake data')
        rc = lib.reefnet_sensusultra_device_get_handshake(dev, hd, SIZE_MEM_HANDSHAKE)
        if rc != 0:
            log.debug('read error rc = {}'.format(rc))
            raise DeviceError('Device communication error')

        log.debug('loading dive data')
        rc = lib.device_dump(dev, dd)
        if rc != 0:
            log.debug('read error rc = {}'.format(rc))
            raise DeviceError('Device communication error')

        return hd.raw + ud.raw + dd.contents.data[:dd.contents.size]


    def dives(self, dump):
        """
        Convert Reefnet Sensus Ultra dive data into UDDF format.
        """
        #dev = self.driver.dev
        #lib = self.driver.lib
        lib = ct.CDLL('libdivecomputer.so.0')

        parser = ct.c_void_p()
        rc = lib.reefnet_sensusultra_parser_create(ct.byref(parser))
        if rc != 0:
            raise DeviceError('Cannot create data parser')
        
        hd = dump.data[:END_HANDSHAKE]
        assert len(hd) == SIZE_MEM_HANDSHAKE, len(hd)
        hdp = _handshake(hd)

        ud = dump.data[START_USER : END_USER]
        assert len(ud) == SIZE_MEM_USER, len(ud)

        dd = ct.create_string_buffer(SIZE_MEM_DATA)
        dd.raw = dump.data[START_DATA:]
        assert len(dd.raw) == SIZE_MEM_DATA, len(dd.raw)

        # boot time = host time - device time (sensus time)
        btime = time.mktime(dump.datetime.timetuple()) - hdp.time

        dq = Queue(10)
        parse_dive = partial(self.parse_dive,
                parser=parser, boot_time=btime, dives=dq)
        f = FuncDive(parse_dive)
        extract_dives = partial(lib.reefnet_sensusultra_extract_dives,
                None, dd, SIZE_MEM_DATA, f, None)

        return _iterate(dq, extract_dives)


    def gases(self, data):
        """
        Return empty tuple - no gas information stored by Sensus Ultra.
        
        :Parameters:
         data
            Sensus Ultra data.
        """
        return ()


    def version(self, data):
        """
        Get Sensus Ultra version from raw data.

        :Parameters:
         data
            Raw dive computer data.
        """
        status = _handshake(data)
        return 'Sensus Ultra %d.%d' % (status.ver2, status.ver1)

    
    def parse_dive(self, buffer, size, fingerprint, fsize, pdata, parser,
            boot_time, dives):
        """
        Callback used by libdivecomputer's library function to extract
        dives from a device and put it into dives queue.

        :Parameters:
         buffer
            Buffer with binary dive data.
         size
            Size of buffer dive data.
         fingerprint
            Fingerprint buffer.
         fsize
            Size of fingerprint buffer.
         pdata
            Parser user data (nothing at the moment).
         parser
            libdivecomputer parser instance.
         boot_time
            Sensus Ultra boot time.
         dives
            Queue of dives to be consumed by caller.
        """
        lib = ct.CDLL('libdivecomputer.so.0')
        lib.parser_set_data(parser, buffer, size)

        header = _dive_header(buffer)
        log.debug('parsing dive: {0}'.format(header))

        # dive time is in seconds since boot time
        # interval is substracted due to depth=0, time=0 sample injection
        st = datetime.fromtimestamp(boot_time - header.interval + header.time)
        log.debug('got dive time: {0}'.format(st))

        samples = []
        parse_sample = partial(self.parse_sample,
                dive_header=header,
                sdata={},
                sq=samples)
        
        f = FuncSample(parse_sample)
        lib.parser_samples_foreach(parser, f, None)

        log.debug('removing {} endcount samples'.format(header.endcount))
        del samples[-header.endcount:]

        # dive summary after endcount removal
        max_depth = max(samples, key=operator.attrgetter('depth')).depth
        min_temp = min(samples, key=operator.attrgetter('temp')).temp
        duration = samples[-1].time + header.interval
        
        # each dive starts below DiveHeader.threshold, therefore inject
        # first sample required by UDDF
        samples.insert(0, kd.Sample(depth=0.0, time=0))

        # each dive ends at about DiveHeader.threshold depth, therefore
        # inject last sample required by UDDF
        samples.append(kd.Sample(depth=0.0, time=duration))

        # finally, create dive data
        dive = kd.Dive(datetime=st, depth=max_depth, duration=duration,
                temp=min_temp, profile=samples)

        try:
            dives.put(dive, timeout=30)
        except Full:
            log.error('could not parse dives due to internal queue timeout')
            return 0

        return 1


    def parse_sample(self, st, sample, pdata, dive_header, sdata, sq):
        """
        Convert dive samples data generated with libdivecomputer library
        into UDDF waypoint structure.

        :Parameters:
         st
            Sample type as specified in parser.h.
         sample
            Sample data.
         pdata
            Parser user data (nothing at the moment).
         dive_header
            Dive header of parsed dive.
         sdata
            Temporary sample data.
         sq
            List of samples. 
        """
        # depth is the last sample type generated by libdivecomputer,
        # create the waypoint then
        if st == SampleType.time:
            sdata['time'] = sample.time
        elif st == SampleType.temperature:
            sdata['temp'] = round(C2K(sample.temperature), 1)
        elif st == SampleType.depth:
            # Sensus Ultra might return negative values near 0, so use max
            sdata['depth'] = round(max(sample.depth, 0), 1)

            s = kd.Sample(**sdata)
            log.debug('got sample {}'.format(sdata))

            sq.append(s)
            sdata.clear() # clear temporary data
        else:
            log.warn('unknown sample type', st)
        return 1


def _handshake(data):
    """
    Convert binary data into HandshakeDump structure.

    :Parameters:
     data
        Binary data.

    """
    return HandshakeDump._make(unpack(FMT_HANDSHAKE, data[:8]))


def _dive_header(data):
    """
    Convert binary data into DiveHeader structure.

    :Parameters:
     data
        Dive binary data.
    """
    return DiveHeader._make(unpack(FMT_DIVE_HEADER, data[:16]))


def _iterate(queue, f):
    """
    Create iterator for stateful function.

    Stateful function pushes items into to the queue, while this function
    pull items from the queue and returns them one by one.

    :Parameters:
     queue
        Queue holding stateful function items.
     f
        Stateful function.
    """
    with ThreadPoolExecutor(max_workers=1) as e:
        fn = e.submit(f)
        
        while not (fn.done() and queue.empty()):
            try:
                n = queue.get(timeout=1)
                yield n
            except Empty:
                if not fn.done():
                    log.warn('su driver possible queue miss')

        if fn.result() == 0:
            raise StopIteration()
        else:
            raise DeviceError('Failed to extract data properly')

# vim: sw=4:et:ai
