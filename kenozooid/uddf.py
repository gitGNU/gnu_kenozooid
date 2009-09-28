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
UDDF file format support.
"""

from lxml import etree as et
from lxml import objectify as eto
from datetime import datetime
from operator import itemgetter
import pwd
import os
import re

import kenozooid

RE_Q = re.compile(r'(\b[a-z]+)')

UDDF = """
<uddf xmlns="http://www.streit.cc/uddf" version="2.2.0">
<generator>
    <name>kenozooid</name>
    <version>%s</version>
    <date></date>
    <time></time>
</generator>
<diver>
<owner>
<personal></personal>
</owner>
</diver>
<profiledata>
</profiledata>
</uddf>
""" % kenozooid.__version__


def create():
    """
    Create UDDF file for dive profile data.
    """
    now = datetime.now()

    name = pwd.getpwnam(os.environ['USER']).pw_gecos.split(' ', 1)
    if len(name) == 1:
        fn = name
        ln = name
    else:
        fn, ln = name

    root = eto.XML(UDDF)

    root.generator.date.year = now.year
    root.generator.date.month = now.month
    root.generator.date.day = now.day
    root.generator.time.hour = now.hour
    root.generator.time.minute = now.minute
    el = root.diver.owner.personal
    el.firstname = fn
    el.lastname = ln

    tree = et.ElementTree(root)
    return tree


def validate(tree):
    """
    Validate UDDF file with UDDF XML Schema.
    """
    schema = et.XMLSchema(et.parse(open('uddf/uddf.xsd')))
    schema.assertValid(tree.getroot())


def compact(tree):
    """
    Remove duplicate dives from UDDF file. Dives are sorted by dive time.
    """
    root = tree.getroot()
    dives = {}
    for dive in tree.findall(q('//dive')):
        dt = get_time(dive)
        if dt not in dives:
            dives[dt] = dive
    del root.profiledata.repetitiongroup[:]
    n = et.SubElement(root.profiledata, q('repetitiongroup'))
    n.dive = [d[1] for d in sorted(dives.items(), key=itemgetter(0))]


def get_time(node):
    """
    Get datetime instance from XML node parsed from UDDF file.

    :Parameters:
     node
        Parsed XML node.
    """
    year = int(node.date.year)
    month = int(node.date.month)
    day = int(node.date.day)
    hour = int(node.time.hour)
    minute = int(node.time.minute)
    return datetime(year, month, day, hour, minute)


def get_dives(fin):
    """
    Get list of dives stored in a file.
    :Parameters:
     fin
        UDDF file.
    """
    f = open(fin)
    tree = eto.parse(f)
    f.close()
    dives = tree.findall(q('//dive'))
    for i, dive in enumerate(dives):
        k = i + 1
        samples = dive.findall(q('samples/waypoint'))
        depths = [float(s.depth.text) for s in samples]
        times = [float(s.divetime) / 60 for s in samples]
        
        yield (k, get_time(dive), times[-1], max(depths))


def q(expr):
    """
    Convert tag names and ElementPath expressions to qualified ones. 
    """
    return RE_Q.sub('{http://www.streit.cc/uddf}\\1', expr)


def has_deco(w):
    """
    Check if a waypoint has deco information.
    """
    return hasattr(w, 'alarm') and any(a.text == 'deco' for a in w.alarm)


def has_temp(w):
    """
    Check if a waypoint has temperature information.
    """
    return hasattr(w, 'temperature')

