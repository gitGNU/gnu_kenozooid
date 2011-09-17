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
The `kenozooid.uddf` module provides support for parsing, searching and
manipulation of data stored in UDDF files.

The functions implemented in this module can be divided into the following
categories

- XML nodes functions
- generic data searching and manipulation functions
- functions for searching and manipulation of diving specific data

Almost each function accepts XPath expression (query) to find or modify
data. Each tag name in an query should be prefixed with 'uddf:' string to
indicate UDDF namespace, i.e. 'uddf:diver', 'uddf:waypoint' - appropriate
namespace mapping for this prefix is defined for each XPath call or during
XML node creation.

The result of parsing or search of data is usually iterator of XML nodes or
data records (named tuples in Python terms) depending on type of function
(see categories above).

Module `lxml` is used for XML parsing and querying with XPath. Full
capabilities of underlying `libxml2' library is used by design. The
ElementTree XML data model is used for XML nodes.
"""

from collections import namedtuple, OrderedDict, Counter
from lxml import etree as et
from functools import partial
from datetime import datetime
from dateutil.parser import parse as dparse
from operator import itemgetter
from uuid import uuid4 as uuid
from copy import deepcopy
import base64
import bz2
import hashlib
import logging
import pkg_resources

import kenozooid

log = logging.getLogger('kenozooid.uddf')

#
# Default UDDF namespace mapping.
#
_NSMAP = {'uddf': 'http://www.streit.cc/uddf/3.0/'}

# Node id formatter
FORMAT_ID = 'id-{}'

#
# Parsing and searching.
#

# XPath query constructor for UDDF data.
XPath = partial(et.XPath, namespaces=_NSMAP)

# XPath queries for default dive data
XP_DEFAULT_DIVE_DATA = (XPath('uddf:informationbeforedive/uddf:datetime/text()'),
    XPath('uddf:informationafterdive/uddf:greatestdepth/text()'),
    XPath('uddf:informationafterdive/uddf:diveduration/text()'),
    XPath('uddf:informationafterdive/uddf:lowesttemperature/text()'))

# XPath queries for default dive profile sample data
XP_DEFAULT_PROFILE_DATA =  (XPath('uddf:divetime/text()'),
        XPath('uddf:depth/text()'),
        XPath('uddf:temperature/text()'),
        XPath('uddf:decostop/@duration'),
        XPath('uddf:decostop/@decodepth'),
        XPath('uddf:alarm/text()'))

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

# XPath queries for default buddy data
XP_DEFAULT_BUDDY_DATA = (XPath('@id'),
        XPath('uddf:personal/uddf:firstname/text()'),
        XPath('uddf:personal/uddf:middlename/text()'),
        XPath('uddf:personal/uddf:lastname/text()'),
        XPath('uddf:personal/uddf:membership/@organisation'),
        XPath('uddf:personal/uddf:membership/@memberid'))

# XPath queries for default dive site data
XP_DEFAULT_SITE_DATA = (XPath('@id'),
        XPath('uddf:name/text()'),
        XPath('uddf:geography/uddf:location/text()'),
        XPath('uddf:geography/uddf:longitude/text()'),
        XPath('uddf:geography/uddf:latitude/text()'))

# XPath query to find a buddy
XP_FIND_BUDDY = XPath('/uddf:uddf/uddf:diver/uddf:buddy[' \
    '@id = $buddy' \
    ' or uddf:personal/uddf:membership/@memberid = $buddy' \
    ' or uddf:personal/uddf:membership/@organisation = $buddy' \
    ' or contains(uddf:personal/uddf:firstname/text(), $buddy)' \
    ' or contains(uddf:personal/uddf:lastname/text(), $buddy)' \
    ']')

# XPath query to find a dive site
XP_FIND_SITE = XPath('/uddf:uddf/uddf:divesite/uddf:site[' \
    '@id = $site' \
    ' or contains(uddf:name/text(), $site)' \
    ' or contains(uddf:geography/uddf:location/text(), $site)' \
    ']')


class RangeError(ValueError):
    """
    Error raised when a range cannot be parsed.

    .. seealso::
        node_range
    """
    pass


def parse(f, query, **params):
    """
    Find XML nodes in UDDF file using XPath query.

    UDDF file can be a file name, file object, URL and basically everything
    what is supported by `lxml` library.

    :Parameters:
     f
        UDDF file to parse.
     query
        XPath expression or XPath object.
     params
        XPath query parameters.

    .. seealso::
        XPath
    """
    log.debug('parsing and searching with query: {}; parameters {}' \
            .format(query, params))
    doc = et.parse(f)
    if isinstance(query, str):
        return xp(doc, query)
    else:
        return (n for n in query(doc, **params))


def xp(node, query):
    """
    Find items with XPath query.

    The query is performed using UDDF namespace.

    Iterator of items (strings, nodes) found by query is returned.
    
    :Parameters:
     node
        Document node or query starting node.
     query
        XPath query.

    .. seealso::
        lxml.etree.Element.xpath
    """
    for n in node.xpath(query, namespaces=_NSMAP):
        yield n 


def xp_first(node, query):
    """
    Get first element found with XPath query.

    The query is performed using UDDF namespace.

    First element is returned or None if it is not found.
    
    :Parameters:
     node
        Document node or query starting node.
     query
        XPath query.

    .. seealso::
        lxml.etree.Element.xpath
    """
    data = xp(node, query)
    return next(data, None)


def xp_last(node, query):
    """
    Get last element found with XPath query.

    The query is performed using UDDF namespace.

    Last element is returned or None if it is not found.
    
    :Parameters:
     node
        Document node or query starting node.
     query
        XPath query.

    .. seealso::
        lxml.etree.Element.xpath
    """
    nodes = node.xpath(query, namespaces=_NSMAP)
    return nodes[-1] if nodes else None


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
        fields = ('datetime', 'depth', 'duration', 'temp')
        queries = XP_DEFAULT_DIVE_DATA
        parsers = (dparse, float, float, float)

    return find_data('Dive', node, fields, queries, parsers)


def dive_profile(node, fields=None, queries=None, parsers=None):
    """
    Specialized function to return generator of dive profiles records.

    By default, dive profile record contains following fields

    time
        dive time in seconds
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
        fields = ('time', 'depth', 'temp', 'deco_time', 'deco_depth', 'alarm')
        queries = XP_DEFAULT_PROFILE_DATA
        parsers = (float, ) * 5 + (str, )

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
    datetime
        Date and time when dive computer dump was obtained.
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
        fields = ('dc_id', 'dc_model', 'datetime', 'data')
        queries = XP_DEFAULT_DUMP_DATA
        parsers = (str, str, dparse, _dump_decode)
    return find_data('DiveComputerDump', node, fields, queries, parsers)


def buddy_data(node, fields=None, queries=None, parsers=None):
    """
    Get dive buddy data.

    The following data is returned by default

    id
        Buddy id.
    fname
        Buddy first name.
    mname
        Buddy middle name.
    lname
        Buddy last name.
    org
        Organization, which a buddy is member of.
    number
        Member number id in the organisation.

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
        fields = ('id', 'fname', 'mname', 'lname', 'org', 'number')
        queries = XP_DEFAULT_BUDDY_DATA
        parsers = (str, ) * 7
    return find_data('Buddy', node, fields, queries, parsers)


def site_data(node, fields=None, queries=None, parsers=None):
    """
    Get dive site data.

    The following data is returned by default

    id
        Dive site id.
    name
        Dive site name.
    location
        Dive site location.
    x
        Dive site longitude.
    y
        Dive site latitude.

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
        fields = ('id', 'name', 'location', 'x', 'y')
        queries = XP_DEFAULT_SITE_DATA
        parsers = (str, str, str, float, float)
    return find_data('DiveSite', node, fields, queries, parsers)


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
    except ValueError as ex:
        raise RangeError('Invalid range %s' % s)
    return ' or '.join(data)


def _field(node, query, parser):
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
    s = base64.b64decode(data.encode())
    return bz2.decompress(s)


#
# Creating UDDF data.
#

# default format for timestamps within UDDF file
FMT_DATETIME = '%Y-%m-%dT%H:%M:%S%z'

DEFAULT_FMT_DIVE_PROFILE = {
    'depth': lambda d: str.format('{0:.1f}', max(d, 0)),
    'temp': partial(str.format, '{0:.1f}'),
}

# basic data for an UDDF file
UDDF_BASIC = """\
<uddf xmlns="http://www.streit.cc/uddf/3.0/" version="3.0.0">
<generator>
    <name>kenozooid</name>
    <manufacturer id='kenozooid'>
      <name>Kenozooid Team</name>
      <contact>
        <homepage>http://wrobell.it-zone.org/kenozooid/</homepage>
      </contact>
    </manufacturer>
    <version>{kzver}</version>
    <datetime></datetime>
</generator>
<diver>
    <owner id='owner'>
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


def create(datetime=datetime.now()):
    """
    Create basic UDDF structure.

    :Parameters:
     datetime
        Timestamp of file creation, current time by default.
    """
    root = et.XML(UDDF_BASIC)

    now = datetime.now()
    n = root.xpath('//uddf:generator/uddf:datetime', namespaces=_NSMAP)[0]
    n.text = _format_time(datetime)
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
        fs = pkg_resources.resource_stream('kenozooid', 'uddf_3.0.1.xsd')
        if hasattr(fs, 'name'):
            log.debug('uddf xsd found: {}'.format(fs.name))
        schema = et.XMLSchema(et.parse(fs))
        try:
            schema.assertValid(doc)
        except et.DocumentInvalid as ex:
            log.info(et.tostring(doc, pretty_print=True))
            raise ex

    et.ElementTree(doc).write(f,
            encoding='utf-8',
            xml_declaration=True,
            pretty_print=True)


def set_data(node, queries, formatters=None, **data):
    """
    Set data of nodes or attributes using XPath queries relative to
    specified XML node.

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

    nodes = {} # created nodes
    attrs = set() # created attributes

    for key, path in queries.items():
        value = data.get(key)
        if value is None:
            continue

        if isinstance(path, str):
            path = [path]
            value = [value]

        for p, v in zip(path, value):
            f = formatters.get(key, str)
            v = f(v)

            attr = None
            tags = p.rsplit('/', 1)
            if tags[-1].startswith('@'):
                attr = tags[-1][1:]  # skip '@'
                p = tags[0] if len(tags) > 1 else None

            n = node
            if p:
                n = nodes.get(p)
                # reuse node created in this call to make t/@a t/@b work,
                # but create new node to not overwrite attribute value
                if n is None or (p, attr) in attrs:
                    *_, n = create_node(p, parent=node)
                    nodes[p] = n
                    attrs.add((p, attr))

            assert n is not None

            if attr:
                n.set(attr, v)
            else:
                n.text = v


def create_node(path, parent=None, append=True):
    """
    Create a hierarchy of nodes using XML nodes path specification.

    Path is a string of node names separated by slash character, i.e. a/b/c
    creates::

        <a><b><c/></b><a>

    If parent node is specified and some part of node hierarchy already
    exists then only non-existant nodes are created, i.e. if parent is
    'x' node in

        <x><y/></x>

    then path 'x/z' modifies XML document as follows

        <x><y/><z/></x>

    :Parameters:
     path
        Hierarchy of nodes.
     parent
         Optional parent node.
    """
    # preserve namespace prefix option... please?!? :/
    T = lambda tag: tag.replace('uddf:', '{' + _NSMAP['uddf'] + '}')
    tags = path.split('/')
    n = parent
    for t in tags:
        is_last = tags[-1] == t

        k = None
        if n is not None:
            k = xp_first(n, t)
        if is_last or k is None:
            k = et.Element(T(t))
        if n is not None:
            if append:
                n.append(k)
            else:
                n.insert(0, k)
        n = k
        yield n


def create_dc_data(node, queries=None, formatters=None,
        dc_id=None, dc_model=None, **data):
    """
    Create dive computer information data in UDDF file.
    """
    _f = ('dc_id', 'dc_model')
    _q = ('@id', 'uddf:model')
    _queries = OrderedDict(zip(_f, _q))
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
            dc_id = FORMAT_ID.format(hashlib.md5(dc_model.encode()).hexdigest())
            data['dc_id'] = dc_id

        # create new dive computer node
        _, dc = create_node('uddf:equipment/uddf:divecomputer', parent=node)
        set_data(dc, _queries, formatters, **data)
    return dc


def create_dive_data(node=None, queries=None, formatters=None, **data):
    """
    Create dive data.

    :Parameters:
     node
        Base node (UDDF root node).
     queries
        Path-like expressions of XML structure to be created.
     formatters
        Dive data formatters.
     data
        Dive data.
    """
    if queries == None:
        bd = data.get('buddies')
        bno = len(bd) if bd else 0
        f = ('site', 'buddies', 'datetime', 'depth', 'duration', 'temp')
        q = ('uddf:informationbeforedive/uddf:link/@ref',
            ['uddf:informationbeforedive/uddf:link/@ref'] * bno,
            'uddf:informationbeforedive/uddf:datetime',
            'uddf:informationafterdive/uddf:greatestdepth',
            'uddf:informationafterdive/uddf:diveduration',
            'uddf:informationafterdive/uddf:lowesttemperature')
        queries = OrderedDict(zip(f, q))
    if formatters == None:
        formatters = {
            'datetime': _format_time,
            'depth': partial(str.format, '{0:.1f}'),
            'duration': partial(str.format, '{0:.0f}'),
            'temp': partial(str.format, '{0:.1f}'),
        }
    _, rg, dn = create_node('uddf:profiledata/uddf:repetitiongroup/uddf:dive',
            parent=node)
    _set_id(rg)
    _set_id(dn)
    set_data(dn, queries, formatters, **data)
    return dn


def create_dive_profile_sample(node, queries=None, formatters=None, **data):
    if queries == None:
        f = ('depth', 'time', 'temp')
        q = ('uddf:depth', 'uddf:divetime', 'uddf:temperature')
        queries = OrderedDict(zip(f, q))
    if formatters == None:
        formatters = DEFAULT_FMT_DIVE_PROFILE

    _, wn = create_node('uddf:samples/uddf:waypoint', parent=node)
    set_data(wn, queries, formatters, **data)
    return wn


def create_dump_data(node, queries=None, formatters=None, **data):
    if queries == None:
        f = ('dc_id', 'datetime', 'data')
        q = ('uddf:link/@ref', 'uddf:datetime', 'uddf:dcdump')
        queries = OrderedDict(zip(f, q))

    if formatters == None:
        formatters = {
            'datetime': _format_time,
            'data': _dump_encode,
        }
        
    _, dcd = create_node('uddf:divecomputercontrol/uddf:divecomputerdump',
            parent=node)
    set_data(dcd, queries, formatters, **data)
    return dcd


def create_buddy_data(node, queries=None, formatters=None, **data):
    """
    Create buddy data.

    :Parameters:
     node
        Base node (UDDF root node).
     queries
        Path-like expressions of XML structure to be created.
     formatters
        Buddy data formatters.
     data
        Buddy data.
     
    """
    if queries == None:
        f = ('id', 'fname', 'mname', 'lname', 'org', 'number')
        q = ('@id',
            'uddf:personal/uddf:firstname',
            'uddf:personal/uddf:middlename',
            'uddf:personal/uddf:lastname',
            'uddf:personal/uddf:membership/@organisation',
            'uddf:personal/uddf:membership/@memberid')
        queries = OrderedDict(zip(f, q))

    if formatters == None:
        formatters = {}

    if 'id' not in data or data['id'] is None:
        data['id'] = uuid().hex
        
    _, buddy = create_node('uddf:diver/uddf:buddy', parent=node)
    set_data(buddy, queries, formatters, **data)
    return buddy


def create_site_data(node, queries=None, formatters=None, **data):
    """
    Create dive site data.

    :Parameters:
     node
        Base node (UDDF root node).
     queries
        Path-like expressions of XML structure to be created.
     formatters
        Dive site data formatters.
     data
        Dive site data.
     
    """
    if queries == None:
        f = ('id', 'name', 'location', 'x', 'y')
        q = ('@id',
            'uddf:name',
            'uddf:geography/uddf:location',
            'uddf:geography/uddf:longitude',
            'uddf:geography/uddf:latitude')
        queries = OrderedDict(zip(f, q))

    if formatters == None:
        formatters = {}

    if 'id' not in data or data['id'] is None:
        data['id'] = uuid().hex
        
    _, site = create_node('uddf:divesite/uddf:site', parent=node)
    set_data(site, queries, formatters, **data)
    return site
        

def _format_time(t):
    """
    Format timestamp into ISO 8601 string compatible with UDDF.
    """
    return format(t, FMT_DATETIME)


def _dump_encode(data):
    """
    Encode dive computer data, so it can be stored in UDDF file.

    The encoded string is returned.
    """
    s = bz2.compress(data)
    return base64.b64encode(s)


#
# Removing UDDF data.
#

def remove_nodes(node, query, **params):
    """
    Remove nodes from XML document using XPath query.

    :Parameters:
     node
        Starting XML node for XPath query.
     query
        XPath query to find nodes to remove.
     params
        XPath query parameters.
    """
    log.debug('node removal with query: {}, params: {}'.format(query, params))
    for n in query(node, **params):
        p = n.getparent()
        p.remove(n)

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
    times = find('//uddf:dive/uddf:informationbeforedive/uddf:datetime/text()')

    dives = {}
    for n, t in zip(nodes, times):
        dt = dparse(t) # don't rely on string representation for sorting
        if dt not in dives:
            dives[dt] = n

    log.debug('removing old repetition groups')
    for rg in rgroups: # cleanup old repetition groups
        pd.remove(rg)
    rg, = create_node('uddf:repetitiongroup', parent=pd)
    _set_id(rg)

    # sort dive nodes by dive time
    log.debug('sorting dives')
    for dt, n in sorted(dives.items(), key=itemgetter(0)):
        rg.append(n)


def copy(node, target):
    """
    Copy node from UDDF document to target node in destination UDDF
    document. Target node becomes parent of node to be copied.

    The copying works under following assumptions

    - whole node is being copied including its descendants
    - if copied nodes reference non-descendant nodes and they do _not_
      exist in destination document, then referencing nodes are _removed_
    - if, due to node removal, its parent node becomes empty, then parent
      is removed, too

    Copy of the node is returned.

    :Parameters:
     node
        Node to copy.
     target
        The future parent of the node to be copied.
    """
    cn = deepcopy(node)

    # get all ids
    s1 = set(xp(target, '//uddf:*/@id'))
    s2 = set(xp(cn, 'descendant-or-self::uddf:*/@id'))
    ids = s1.union(s2)

    # get referencing nodes
    nodes = list(xp(cn, 'descendant-or-self::uddf:*[@ref]'))
    refs = set(k.get('ref') for k in nodes)

    left = refs - ids
    log.debug('references to remove: {} = {} - {}'.format(left, refs, ids))

    if cn.get('ref') in left:
        raise ValueError('Node to copy references non-existing node')

    # remove referencing nodes to missing data
    to_remove = (n for n in nodes if n.get('ref') in left)
    assert cn.getparent() is None
    for n in to_remove:
        p = n.getparent()
        while p is not None and len(p) == 1:
            n = p
            p = n.getparent()
        if p is not None:
            p.remove(n)

    target.append(cn)
    return cn


def _set_id(node):
    """
    Generate id for a node if there is no id yet.

    :Parameters:
     node
        Node for which id should be generated.
    """
    if node.get('id') is None:
        node.set('id', FORMAT_ID.format(uuid().hex))


# vim: sw=4:et:ai
