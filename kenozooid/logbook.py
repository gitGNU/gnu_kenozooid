#
# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2011 by Artur Wroblewski <wrobell@pld-linux.org>
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
Dive logbook functionality.

Dive, dive site and buddy data display and management is implemented.
"""

import lxml.etree as et
import os.path
import logging

import kenozooid.uddf as ku
from kenozooid.util import min2str, FMT_DIVETIME
from kenozooid.units import K2C

log = logging.getLogger('kenozooid.logbook')

def list_dives(fin):
    """
    Get generator of preformatted dive data.

    The dives are fetched from logbook file and for 
    each dive a tuple of formatted dive information
    is returned

    - date and time of dive, i.e. 2011-03-19 14:56
    - maximum depth, i.e. 6.0m
    - duration of dive, i.e. 33:42
    - temperature, i.e. 8.2°C

    :Parameters:
     fin
        Logbook file in UDDF format.
    """
    dives = (ku.dive_data(n) for n in ku.parse(fin, '//uddf:dive'))

    for dive in dives:
        try:
            duration = min2str(dive.duration / 60.0)
            depth = '{:.1f}m'.format(dive.depth)
            temp = ''
            if dive.temp is not None:
                temp = '{:.1f}\u00b0C'.format(K2C(dive.temp))
            yield (format(dive.time, FMT_DIVETIME), depth,
                    duration, temp)
        except TypeError as ex:
            log.debug(ex)
            log.warn('invalid dive data, skipping dive')


def add_dive(lfile, time=None, depth=None, duration=None, dive_no=None,
        pfile=None, qsite=None, qbuddy=None):
    """
    Add new dive to logbook file.

    The logbook file is created if it does not exist.

    If dive number is specified and dive cannot be found then ValueError
    exception is thrown.

    :Parameters:
     lfile
        Logbook file.
     time
        Dive time.
     depth
        Dive maximum depth.
     duration
        Dive duration (in minutes).
     dive_no
        Dive number in dive profile file.
     pfile
        Dive profile file.
     qsite
        Dive site search term.
     qbuddy
        Buddy search term.
    """
    dive = None # obtained from profile file

    if os.path.exists(lfile):
        doc = et.parse(lfile).getroot()
    else:
        doc = ku.create()

    site_id = None
    if qsite:
        nodes = ku.parse(lfile, ku.XP_FIND_SITE, site=qsite)
        n = next(nodes, None)
        if n is None:
            raise ValueError('Cannot find dive site in logbook file')
        if next(nodes, None) is not None:
            raise ValueError('Found more than one dive site')

        site_id = n.get('id')

    buddy_id = None
    if qbuddy:
        nodes = ku.parse(lfile, ku.XP_FIND_BUDDY, site=qbuddy)
        n = next(nodes, None)
        if n is None:
            raise ValueError('Cannot find buddy in logbook file')
        if next(nodes, None) is not None:
            raise ValueError('Found more than one buddy')

        buddy_id = n.get('id')

    if dive_no is not None and pfile is not None:
        q = ku.XPath('//uddf:dive[position() = $no]')
        dives = ku.parse(pfile, q, no=dive_no)
        dive = next(dives, None)
        if dive is None:
            raise ValueError('Cannot find dive in dive profile data')

        assert next(dives, None) is None, 'only one dive expected'

        _, rg = ku.create_node('uddf:profiledata/uddf:repetitiongroup',
                parent=doc)
        ku.copy(dive, rg)

    elif (time, depth, duration) is not (None, None, None):
        duration = int(duration * 60)
        ku.create_dive_data(doc, time=time, depth=depth,
                duration=duration, site=site_id)
    else:
        raise ValueError('Dive data or dive profile needs to be provided')

    ku.reorder(doc)
    ku.save(doc, lfile)


# vim: sw=4:et:ai
