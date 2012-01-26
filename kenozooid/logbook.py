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
Dive logbook functionality.

Dive, dive site and buddy data display and management is implemented.
"""

import lxml.etree as et
import os.path
import logging
import pkg_resources

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
    - dive average depth, i.e. 2.0m
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
            avg_depth = ''
            if dive.avg_depth is not None:
                avg_depth = '{:.1f}m'.format(dive.avg_depth)
            yield (format(dive.datetime, FMT_DIVETIME), depth, avg_depth,
                    duration, temp)
        except TypeError as ex:
            log.debug(ex)
            log.warn('invalid dive data, skipping dive')


# split into add_dive and copy_dive
# extract buddies adding and setting dive site functionality into separate
# functions
def add_dive(lfile, datetime=None, depth=None, duration=None, dive_no=None,
        pfile=None, qsite=None, qbuddies=()):
    """
    Add new dive to logbook file.

    The logbook file is created if it does not exist.

    If dive number is specified and dive cannot be found then ValueError
    exception is thrown.

    :Parameters:
     lfile
        Logbook file.
     datetime
        Dive date and time.
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
     qbuddies
        Buddy search terms.
    """
    dive = None # obtained from profile file

    if os.path.exists(lfile):
        doc = et.parse(lfile).getroot()
    else:
        doc = ku.create()

    if qbuddies is None:
        qbuddies = []

    site_id = None
    if qsite:
        nodes = ku.parse(lfile, ku.XP_FIND_SITE, site=qsite)
        n = next(nodes, None)
        if n is None:
            raise ValueError('Cannot find dive site in logbook file')
        if next(nodes, None) is not None:
            raise ValueError('Found more than one dive site')

        site_id = n.get('id')

    buddy_ids = []
    log.debug('looking for buddies {}'.format(qbuddies))
    for qb in qbuddies:
        log.debug('looking for buddy {}'.format(qb))
        nodes = ku.parse(lfile, ku.XP_FIND_BUDDY, buddy=qb)
        n = next(nodes, None)
        if n is None:
            raise ValueError('Cannot find buddy {} in logbook file'.format(qb))
        if next(nodes, None) is not None:
            raise ValueError('Found more than one buddy for {}'.format(qb))

        buddy_ids.append(n.get('id'))

    if dive_no is not None and pfile is not None:
        log.debug('creating dive with profile')
        q = ku.XPath('//uddf:dive[position() = $no]')
        dives = ku.parse(pfile, q, no=dive_no)
        dive = next(dives, None)
        if dive is None:
            raise ValueError('Cannot find dive in dive profile data')

        assert next(dives, None) is None, 'only one dive expected'

        _, rg = ku.create_node('uddf:profiledata/uddf:repetitiongroup',
                parent=doc)
        dive = ku.copy(dive, rg)

        n = ku.xp_first(dive, 'uddf:informationbeforedive')

        # reference buddies first
        for b_id in buddy_ids:
            l, *_ = ku.create_node('uddf:link', parent=n, append=False)
            l.set('ref', b_id)

        # set reference to dive site (as first link)
        if site_id:
            l, *_ = ku.create_node('uddf:link', parent=n, append=False)
            l.set('ref', site_id)

    elif (datetime, depth, duration) is not (None, None, None):
        log.debug('creating dive data')
        duration = int(duration * 60)
        ku.create_dive_data(doc, datetime=datetime, depth=depth,
                duration=duration, site=site_id, buddies=buddy_ids)
    else:
        raise ValueError('Dive data or dive profile needs to be provided')

    ku.reorder(doc)
    ku.save(doc, lfile)


def upgrade_file(fin):
    """
    Upgrade UDDF file to newer version.

    :Parameters:
     fin
        File object with UDDF data to upgrade.
    """
    current = (3, 1)
    versions = ((3, 0), )
    xslt = ('uddf-3.0.0-3.1.0.xslt',)

    ver = ku.get_version(fin)
    if ver == current:
        raise ValueError('File is at UDDF {}.{} version already' \
            .format(*current))
    try:
        k = versions.index(ver)
    except ValueError:
        raise ValueError('Cannot upgrade UDDF file version {}.{}'.format(*ver))

    doc = et.parse(fin)
    for i in range(k, len(versions)):
        fs = pkg_resources.resource_stream('kenozooid', 'uddf/{}'.format(xslt[i]))
        transform = et.XSLT(et.parse(fs))
        doc = transform(doc)
    return doc

# vim: sw=4:et:ai
