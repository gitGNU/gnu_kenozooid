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
import itertools
ichain = itertools.chain.from_iterable
from itertools import zip_longest as lzip
from operator import itemgetter
import pkg_resources

import kenozooid.uddf as ku
from kenozooid.util import min2str, FMT_DIVETIME
from kenozooid.units import K2C

log = logging.getLogger('kenozooid.logbook')


def find_dive_nodes(files, nodes=None, dives=None):
    """
    Find dive nodes in UDDF files using optional numeric ranges or total
    dive number as search parameters.

    The collection of dive nodes is returned.

    :Parameters:
     files
        Collection of UDDF files.
     nodes
        Numeric ranges of nodes, `None` if all nodes.
     dives
        Numeric range of total dive number, `None` if any dive.

    .. seealso:: :py:func:`parse_range`
    .. seealso:: :py:func:`find_dives`
    """
    nodes = [] if nodes is None else nodes
    data = (ku.find(f, ku.XP_FIND_DIVES, nodes=q, dives=dives) \
        for q, f in lzip(nodes, files))
    return ichain(data)


def find_dive_gas_nodes(files, nodes=None):
    """
    Find gas nodes referenced by dives in UDDF files using optional node
    ranges as search parameter.

    The collection of gas nodes is returned.

    :Parameters:
     files
        Collection of UDDF files.
     nodes
        Numeric ranges of nodes, `None` if all nodes.

    .. seealso:: :py:func:`parse_range`
    """
    nodes = [] if nodes is None else nodes
    data = (ku.find(f, ku.XP_FIND_DIVE_GASES, nodes=q) \
        for q, f in lzip(nodes, files))
    nodes_by_id = ((n.get('id'), n) for n in ichain(data))
    return dict(nodes_by_id).values()


def find_dives(files, nodes=None, dives=None):
    """
    Find dive data in UDDF files using optional node ranges or total dive
    number as search parameters.

    The collection of dive data is returned.

    :Parameters:
     files
        Collection of UDDF files.
     nodes
        Numeric ranges of nodes, `None` if all nodes.
     dives
        Numeric range of total dive number, `None` if any dive.

    .. seealso:: :py:func:`parse_range`
    .. seealso:: :py:func:`find_dive_nodes`
    """
    return (ku.dive_data(n) for n in find_dive_nodes(files, nodes, dives))
        

def list_dives(dives):
    """
    Get generator of preformatted dive data.

    The dives are fetched from logbook file and for 
    each dive a tuple of formatted dive information
    is returned

    - dive number, i.e. 102
    - date and time of dive, i.e. 2011-03-19 14:56
    - maximum depth, i.e. 6.0m
    - dive average depth, i.e. 2.0m
    - duration of dive, i.e. 33:42
    - temperature, i.e. 8.2°C

    :Parameters:
     dives
        Collection of dive data.
    """
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
            yield (dive.number, format(dive.datetime, FMT_DIVETIME), depth,
                avg_depth, duration, temp)
        except TypeError as ex:
            log.debug(ex)
            log.warn('invalid dive data, skipping dive')


def add_dive(dive, lfile, qsite=None, qbuddies=()):
    """
    Add new dive to logbook file.

    The logbook file is created if it does not exist.

    If dive number is specified and dive cannot be found then ValueError
    exception is thrown.

    :Parameters:
     dive
        Dive data.
     lfile
        Logbook file.
     qsite
        Dive site search term.
     qbuddies
        Buddy search terms.
    """
    if os.path.exists(lfile):
        doc = et.parse(lfile).getroot()
    else:
        doc = ku.create()

    if qbuddies is None:
        qbuddies = []

    site_id = None
    if qsite:
        nodes = ku.find(lfile, ku.XP_FIND_SITE, site=qsite)
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
        nodes = ku.find(lfile, ku.XP_FIND_BUDDY, buddy=qb)
        n = next(nodes, None)
        if n is None:
            raise ValueError('Cannot find buddy {} in logbook file'.format(qb))
        if next(nodes, None) is not None:
            raise ValueError('Found more than one buddy for {}'.format(qb))

        buddy_ids.append(n.get('id'))

    log.debug('creating dive data')
    ku.create_dive_data(doc, datetime=dive.datetime, depth=dive.depth,
                duration=dive.duration, site=site_id, buddies=buddy_ids)

    ku.reorder(doc)
    ku.save(doc, lfile)


def upgrade_file(fin):
    """
    Upgrade UDDF file to newer version.

    :Parameters:
     fin
        File with UDDF data to upgrade.
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

    doc = ku.parse(fin, ver_check=False)
    for i in range(k, len(versions)):
        fs = pkg_resources.resource_stream('kenozooid', 'uddf/{}'.format(xslt[i]))
        transform = et.XSLT(et.parse(fs))
        doc = transform(doc)
    return doc


def copy_dives(files, nodes, n_dives, lfile):
    """
    Copy dive nodes to logbook file.

    The logbook file is created if it does not exist.

    :Parameters:
     files
        Collection of files.
     nodes
        Collection of dive ranges.
     n_dives
        Numeric range of total dive number, `None` if any dive.
     lfile
        Logbook file.
    """
    if os.path.exists(lfile):
        doc = et.parse(lfile).getroot()
    else:
        doc = ku.create()

    dives = find_dive_nodes(files, nodes, n_dives)
    gases = find_dive_gas_nodes(files, nodes)

    _, rg = ku.create_node('uddf:profiledata/uddf:repetitiongroup',
            parent=doc)
    gn = ku.xp_first(doc, 'uddf:gasdefinitions')
    existing = gn is not None
    if not existing:
        *_, gn = ku.create_node('uddf:gasdefinitions', parent=doc)

    with ku.NodeCopier(doc) as nc:
        copied = False
        for n in gases:
            copied = nc.copy(n, gn) is not None or copied
        if not existing and not copied:
            p = gn.getparent()
            p.remove(gn)

        copied = False
        for n in dives:
            copied = nc.copy(n, rg) is not None or copied

        if copied:
            ku.reorder(doc)
            ku.save(doc, lfile)
        else:
            log.debug('no dives copied')


def enum_dives(files, total=1):
    """
    Enumerate dives with day dive number (when UDDF 3.2 is introduced) and
    total dive number.

    :Parameters:
     files
        Collection of UDDF files having dives to enumerate.
     total
        Start of total dive number.
    """
    fields = ('id', 'date')
    queries = (
        ku.XPath('@id'),
        ku.XPath('uddf:informationbeforedive/uddf:datetime/text()'),
    )
    parsers = (str, lambda dt: ku.dparse(dt).date())

    fnodes = ((f, n) for f in files for n in
        ku.find(f, ku.XP_FIND_DIVES, nodes=None, dives=None))
    data = ((f, ku.dive_data(n, fields, queries, parsers)) for f, n in fnodes)
    data = ((item[0], item[1].id, item[1].date) for item in data) # flatten data
    data = sorted(data, key=itemgetter(2))

    # enumerate dives with _day_ dive number and flatten the groups
    data = ichain(enumerate(g, 1) for k, g in
        itertools.groupby(data, itemgetter(2)))

    # enumerate dives with total dive number and transform into
    #   { (f, id) => (n, k) }
    cache = dict(((v[0], v[1]), (n, k)) for n, (k, v) in enumerate(data, total))

    # update data
    for f in files:
        doc = ku.parse(f)
        for n in ku.XP_FIND_DIVES(doc, nodes=None, dives=None):
            id = n.get('id')
            dnn = ku.xp_first(n, 'uddf:informationbeforedive/uddf:divenumber')
            if dnn is None:
                pn = ku.xp_first(n, 'uddf:informationbeforedive/uddf:internaldivenumber')
                if pn is None:
                    pn = ku.xp_first(n, 'uddf:informationbeforedive/uddf:datetime')
                *_, dnn = ku.create_node('uddf:divenumber')
                pn.addprevious(dnn)
            dnn.text = str(cache[f, id][0])
        ku.save(doc.getroot(), f)


# vim: sw=4:et:ai
