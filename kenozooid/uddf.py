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
UDDF file format support. The code below is divided into data lookup, data
creation and data post-processing sections.

UDDF files are basis for Kenozooid data model.

The UDDF data is parsed and queried with XPath. The result of a query is
generator[1] of records (named tuples in Python terms), which should
guarantee memory efficiency[2].

Module `lxml` is used for XML parsing and XPath querying and full
capabilities of underlying `libxml2' library should be used. The
ElementTree XML data model is used.

Namespace Support
=================
Each tag name in every XPath expression should be prefixed with `uddf`
string. Appropriate namespace mapping for this prefix is defined for each
XPath query.

Remarks
=======
[1] Ideally, it is generator. Some of the routines implemented in this
module need to be optimized to _not_ return lists.

TODO: More research is needed to cache results of some of the queries. 
"""

from collections import namedtuple
from lxml import etree as et
from functools import partial
from datetime import datetime
from dateutil.parser import parse as dparse
from operator import itemgetter
import base64
import bz2
import hashlib
import logging

import kenozooid

log = logging.getLogger('kenozooid.uddf')

#
# Default UDDF namespace mapping.
#
_NSMAP = {'uddf': 'http://www.streit.cc/uddf'}

#
# Parsing and searching.
#

# XPath query constructor for UDDF data.
XPath = partial(et.XPath, namespaces=_NSMAP)

# XPath queries for default dive data
XP_DEFAULT_DIVE_DATA = (XPath('uddf:datetime/text()'), )

# XPath queries for default dive profile sample data
XP_DEFAULT_PROFILE_DATA =  (XPath('uddf:divetime/text()'),
        XPath('uddf:depth/text()'),
        XPath('uddf:temperature/text()'))

# XPath query to locate dive profile sample
XP_WAYPOINT = XPath('.//uddf:waypoint')

# XPath queries for default dive computer dump data
XP_DEFAULT_DUMP_DATA = (XPath('uddf:link/@ref'),
        # //uddf:divecomputerdump[position()] gives current()
        XPath('../../uddf:diver/uddf:owner//uddf:divecomputer[' \
                '@id = //uddf:divecomputerdump[position()]/uddf:link/@ref' \
            ']/uddf:model/text()'),
        XPath('uddf:datetime/text()'),
        XPath('uddf:dcdump/text()'))


class RangeError(ValueError):
    """
    Error raised when a range cannot be parsed.

    .. seealso::
        node_range
    """
    pass


def parse(f, query):
    """
    Find nodes in UDDF file using XPath query.

    UDDF file can be a file name, file object, URL or basically everything
    what is supported by `lxml`.

    :Parameters:
     f
        UDDF file to parse.
     query
        XPath expression.
    """
    log.debug('parsing and searching with with query: {0}'.format(query))
    doc = et.parse(f)
    for n in xpath(doc, query):
        yield n


def xpath(node, query):
    """
    Perform XPath query in UDDF namespace on specified node.

    The result is data returned by lxml.etree.Element.xpath.
    
    :Parameters:
     node
        Node to be queried.
     query
        XPath query.

    .. seealso::
        lxml.etree.Element.xpath
    """
    return node.xpath(query, namespaces=_NSMAP)


def xpath_first(node, query):
    """
    Find first element with XPath query in UDDF namespace on specified
    node.

    First element is returned or None if it was not found.
    
    :Parameters:
     node
        Node to be queried.
     query
        XPath query.

    .. seealso::
        lxml.etree.Element.xpath
    """
    data = xpath(node, query)
    if data:
        return data[0]
    else:
        return  None


def find_data(name, node, fields, queries, parsers, nquery=None):
    """
    Find data records starting from specified XML node.

    A record type (namedtuple) is created with specified fields. The data
    of a record is retrieved with XPath expression objects, which is
    converted from string to appropriate type using parsers.

    A parser can be any type or function, i.e. `float`, `int` or
    `dateutil.parser.parse`.

    If XML node is too high to execture XPath expression objects, then the
    basis for field queries can be relocated with `nquery` parameter. If
    `nquery` parameter is not specified, then only one record is returned.
    Otherwise it is generator of records.

    The length of fields, field queries and field parsers should be the same.

    :Parameters:
     name
        Name of the record to be created.
     node
        XML node.
     fields
        Names of fields to be created in a record.
     queries
        XPath expression objects for each field to retrieve its value.
     parsers
        Parsers of field values to be created in a record.
     nquery
        XPath expression object to relocate from node to more appropriate
        position in XML document for record data retrieval.

    .. seealso::
        dive_data
        dive_profile
    """
    T = namedtuple(name, ' '.join(fields))._make
    if nquery:
        data = nquery(node)
        return (_record(T, n, queries, parsers) for n in data)
    else:
        return _record(T, node, queries, parsers)


def dive_data(node, fields=None, queries=None, parsers=None):
    """
    Specialized function to return record of a dive data.

    At the moment record of dive data contains dive start time only, by
    default. It should be enhanced in the future to return more rich data
    record.

    Dive record data can be reconfigured with optional fields, field
    queries and field parsers parameters.

    :Parameters:
     node
        XML node.
     fields
        Names of fields to be created in a record.
     queries
        XPath expression object for each field to retrieve its value.
     parsers
        Parsers field values to be created in a record.

    .. seealso::
        find_data
    """

    if fields is None:
        fields = ('time', )
        queries = XP_DEFAULT_DIVE_DATA
        parsers = (dparse, )

    return find_data('Dive', node, fields, queries, parsers)


def dive_profile(node, fields=None, queries=None, parsers=None):
    """
    Specialized function to return generator of dive profiles records.

    By default, dive profile record contains following fields

    time
        dive time is seconds
    depth
        dive depth in meters
    temp
        temperature in Kelvins

    Dive profile record data can be reconfigured with optional fields,
    field queries and field parsers parameters.

    :Parameters:
     node
        XML node.
     fields
        Names of fields to be created in a record.
     queries
        XPath expression objects for each field to retrieve its value.
     parsers
        Parsers of field values to be created in a record.

    .. seealso::
        find_data
    """
    if fields is None:
        fields = ('time', 'depth', 'temp')
        queries = XP_DEFAULT_PROFILE_DATA
        parsers = (float, ) * 3

    return find_data('Sample', node, fields, queries, parsers,
            nquery=XP_WAYPOINT)


def dump_data(node, fields=None, queries=None, parsers=None):
    """
    Get dive computer dump data.

    The following data is returned

    dc_id
        Dive computer id.
    dc_model
        Dive computer model information.
    time
        Time when dive computer dump was obtained.
    data
        Dive computer dump data.

    :Parameters:
     node
        XML node.
     fields
        Names of fields to be created in a record.
     queries
        XPath expression objects for each field to retrieve its value.
     parsers
        Parsers of field values to be created in a record.

    .. seealso::
        find_data
    """
    if fields is None:
        fields = ('dc_id', 'dc_model', 'time', 'data')
        queries = XP_DEFAULT_DUMP_DATA
        parsers = (str, str, dparse, _dump_decode)
    return find_data('DiveComputerDump', node, fields, queries, parsers)


def node_range(s):
    """
    Parse textual representation of number range into XPath expression.

    Examples of a ranges

    >>> node_range('1-3,5')
    '1 <= position() and position() <= 3 or position() = 5'

    >>> node_range('-3,10')
    'position() <= 3 or position() = 10'

    Example of infinite range

    >>> node_range('20-')
    '20 <= position()'

    :Parameters:
     s
        Textual representation of number range.
    """
    data = []
    try:
        for r in s.split(','):
            d = r.split('-')
            if len(d) == 1:
                data.append('position() = %d' % int(d[0]))
            elif len(d) == 2:
                p1 = d[0].strip()
                p2 = d[1].strip()
                if p1 and p2:
                    data.append('%d <= position() and position() <= %d' \
                            % (int(p1), int(p2)))
                elif p1 and not p2:
                    data.append('%d <= position()' % int(p1))
                elif not p1 and p2:
                    data.append('position() <= %d' % int(p2))
            else:
                raise RangeError('Invalid range %s' % s)
    except ValueError, ex:
        raise RangeError('Invalid range %s' % s)
    return ' or '.join(data)


def _field(node, query, parser=float):
    """
    Find text value of a node starting from specified XML node.

    The text value is converted with function `t` and then returned.

    If node is not found, then `None` is returned.

    :Parameters:
     node
        XML node.
     query
        XPath expression object to find node with text value.
     parser
        Parser to convert text value to requested type.
    """
    data = query(node)
    if data:
        return parser(data[0])


def _record(rt, node, queries, parsers):
    """
    Create record with data.

    The record data is found with XPath expressions objects starting from
    XML node.  The data is converted to their appropriate type using
    parsers.

    :Parameters:
    rt
        Record type (named tuple) of record data.
    node
        XML node.
     queries
        XPath expression objects for each field to retrieve its value.
     parsers
        Parsers of field values to be created in a record.
    """
    return rt(_field(node, f, p) for f, p in zip(queries, parsers))


def _dump_decode(data):
    """
    Decode dive computer data, which is stored in UDDF dive computer dump
    file.
    """
    s = base64.b64decode(data)
    return bz2.decompress(s)


#
# Creating UDDF data.
#

# default format for timestamps within UDDF file
FMT_DATETIME = '%Y-%m-%d %H:%M:%S%z'

DEFAULT_FMT_DIVE_PROFILE = {
    'depth': lambda d: str.format('{0:.1f}', max(d, 0)),
    'temp': partial(str.format, '{0:.1f}'),
}

# basic data for an UDDF file
UDDF_BASIC = """\
<uddf xmlns="http://www.streit.cc/uddf" version="3.0.0">
<generator>
    <name>kenozooid</name>
    <version>{kzver}</version>
    <manufacturer>
      <name>Kenozooid Team</name>
      <contact>
        <homepage>http://wrobell.it-zone.org/kenozooid/</homepage>
      </contact>
    </manufacturer>
    <datetime></datetime>
</generator>
<diver>
    <owner>
        <personal>
            <firstname>Anonymous</firstname>
            <lastname>Guest</lastname>
        </personal>
    </owner>
</diver>
</uddf>
""".format(kzver=kenozooid.__version__)

###<equipment>
###    <divecomputer id=''>
###        <model></model>
###    </divecomputer>
###</equipment>


def create(time=datetime.now()):
    """
    Create basic UDDF structure.

    :Parameters:
     time
        Timestamp of file creation, current time by default.
    """
    root = et.XML(UDDF_BASIC)

    now = datetime.now()
    n = root.xpath('//uddf:generator/uddf:datetime', namespaces=_NSMAP)[0]
    n.text = _format_time(time)
    return root


def save(doc, f, validate=True):
    """
    Save UDDF data to a file.

    A file can be a file name, file like object or anything supported by
    `lxml` for writing.

    :Parameters:
     doc
        UDDF document to save.
     f
        UDDF output file.
     validate
        Validate UDDF file before saving if set to True.
    """
    log.debug('cleaning uddf file')
    #et.deannotate(doc)
    et.cleanup_namespaces(doc)

    if validate:
        log.debug('validating uddf file')
        #schema = et.XMLSchema(et.parse(open('uddf/uddf.xsd')))
        #schema.assertValid(doc.getroot())

    et.ElementTree(doc).write(f,
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=True)


def create_data(node, queries, formatters=None, **data):
    """
    Create XML data relative to specified XML node.

    The data values are converted to string with formatters functions.

    :Parameters:
     node
        XML node.
     queries
        Path-like expressions of XML structure to be created.
     formatters
        Data formatters.
     data
        Data values to be set within XML document.
    """
    if formatters is None:
        formatters = {}

    for key, p in queries.items():

        value = data.get(key)
        if value is None:
            continue

        f = formatters.get(key, str)
        value = f(value)

        attr = None
        tags = p.rsplit('/', 1)
        if tags[-1].startswith('@'):
            attr = tags[-1][1:]
            p = tags[0] if len(tags) > 1 else None

        n = node
        if p:
            nodes = list(create_node(p, parent=node))
            n = nodes[-1]
        if attr:
            n.set(attr, value)
        else:
            n.text = value


def create_node(path, parent=None):
    # preserve namespace prefix option... please?!? :/
    T = lambda tag: tag.replace('uddf:', '{' + _NSMAP['uddf'] + '}')
    tags = path.split('/')
    n = parent
    for t in tags:
        is_last = tags[-1] == t
        exists = False

        t = T(t)

        if n is not None:
            for k in n:
                if k.tag == t:
                    exists = True
                    break
        if is_last or not exists:
            k = et.Element(t)
        if n is not None:
            n.append(k)
        n = k
        yield n


def create_dc_data(node, queries=None, formatters=None,
        dc_id=None, dc_model=None, **data):
    """
    Create dive computer information data in UDDF file.
    """
    _queries = {
        'dc_id': '@id',
        'dc_model': 'uddf:model',
    }
    if queries is not None:
        _queries.update(queries)

    data['dc_id'] = dc_id
    data['dc_model'] = dc_model

    dc = None

    if dc_id:
        xp = XPath('uddf:equipment/uddf:divecomputer[id@$dc_id]')
        nodes = xp(node, dc_id=dc_id)
        if nodes:
            dc = nodes[0]
    else:
        xp = XPath('uddf:equipment/uddf:divecomputer[uddf:model/text() = $dc_model]')
        nodes = xp(node, dc_model=dc_model)
        if nodes:
            dc = nodes[0]

    if dc is None:
        if not dc_id:
            dc_id = 'id' + hashlib.md5(str(dc_model)).hexdigest()
            data['dc_id'] = dc_id

        # create new dive computer node
        _, dc = create_node('uddf:equipment/uddf:divecomputer', parent=node)
        create_data(dc, _queries, formatters, **data)
    return dc


def create_dive_data(node=None, queries=None, formatters=None, **data):
    if queries == None:
        queries = {
            'time': 'uddf:datetime',
        }
    if formatters == None:
        formatters = {
            'time': _format_time,
        }
    _, _, dn = create_node('uddf:profiledata/uddf:repetitiongroup/uddf:dive',
            parent=node)
    create_data(dn, queries, formatters, **data)
    return dn


def create_dive_profile_sample(node, queries=None, formatters=None, **data):
    if queries == None:
        queries = {
            'depth': 'uddf:depth',
            'time': 'uddf:divetime',
            'temp': 'uddf:temperature',
        }
    if formatters == None:
        formatters = DEFAULT_FMT_DIVE_PROFILE

    _, wn = create_node('uddf:samples/uddf:waypoint', parent=node)
    create_data(wn, queries, formatters, **data)
    return wn


def create_dump_data(node, queries=None, formatters=None, **data):
    if queries == None:
        queries = {
            'dc_id': 'uddf:link/@ref',
            'time': 'uddf:datetime',
            'data': 'uddf:dcdump',
        }
    if formatters == None:
        formatters = {
            'time': _format_time,
            'data': _dump_encode,
        }
        
    _, dcd = create_node('uddf:divecomputercontrol/uddf:divecomputerdump',
            parent=node)
    create_data(dcd, queries, formatters, **data)
    return dcd
        

def _format_time(t):
    """
    Format timestamp into ISO 8601 string compatible with UDDF.
    """
    return t.strftime(FMT_DATETIME)


def _dump_encode(data):
    """
    Encode dive computer data, so it can be stored in UDDF file.

    The encoded string is returned.
    """
    s = bz2.compress(data)
    return base64.b64encode(s)


#
# Processing UDDF data.
#


def reorder(doc):
    """
    Reorder and cleanup dives in UDDF document.

    Following operations are being performed

    - dives are sorted by dive start time 
    - duplicate dives and repetition groups are removed

    :Parameters:
     doc
        UDDF document.

    TODO: Put dives into appropriate repetition groups.
    """
    find = partial(doc.xpath, namespaces=_NSMAP)

    profiles = find('//uddf:profiledata')
    rgroups = find('//uddf:profiledata/uddf:repetitiongroup')
    if not profiles or not rgroups:
        raise ValueError('No profile data to reorder')
    pd = profiles[0]

    nodes = find('//uddf:dive')
    times = find('//uddf:dive/uddf:datetime/text()')

    dives = {}
    for n, t in zip(nodes, times):
        dt = dparse(t) # don't rely on string representation for sorting
        if dt not in dives:
            dives[dt] = n

    log.debug('removing old repetition groups')
    for rg in rgroups: # cleanup old repetition groups
        pd.remove(rg)
    rg, = create_node('uddf:repetitiongroup', parent=pd)

    # sort dive nodes by dive time
    log.debug('sorting dives')
    for dt, n in sorted(dives.items(), key=itemgetter(0)):
        rg.append(n)


# vim: sw=4:et:ai
