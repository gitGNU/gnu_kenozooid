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
UDDF file format tests.
"""

import unittest
from lxml import etree
from lxml.objectify import parse as loparse
from datetime import datetime
from StringIO import StringIO

from kenozooid.uddf import create, compact, get_time, q

class UDDFTestCase(unittest.TestCase):
    """
    UDDF file format tests.
    """
    def test_creation(self):
        """Test UDDF creation
        """
        tree = create()
        data = etree.tostring(tree.getroot())
        self.assertTrue('2.2.0' in data)
        self.assertTrue('Kenozooid' in data)


    def test_time_parsing(self):
        """Test UDDF time parsing
        """
        tree = loparse(StringIO("""
<uddf xmlns="http://www.streit.cc/uddf">
<profiledata>
<repetitiongroup>
<dive>
    <date>
        <year>2009</year>
        <month>3</month>
        <day>2</day>
    </date>
    <time>
        <hour>23</hour>
        <minute>2</minute>
    </time>
</dive>
</repetitiongroup>
</profiledata>
</uddf>
"""))
        dt = get_time(tree.find(q('//dive')))
        self.assertEquals(datetime(2009, 3, 2, 23, 2), dt)


    def test_q(self):
        """Test conversion to qualified tag names and ElementPath expressions"""
        self.assertEquals('{http://www.streit.cc/uddf}name', q('name'))
        self.assertEquals('//{http://www.streit.cc/uddf}name', q('//name'))
        self.assertEquals('{http://www.streit.cc/uddf}samples/' \
                '{http://www.streit.cc/uddf}waypoint', q('samples/waypoint'))


class UDDFCompactTestCase(unittest.TestCase):
    def test_uddf_compact(self):
        """Test UDDF compact
        """
        tree = loparse(StringIO("""
<uddf xmlns="http://www.streit.cc/uddf">
<profiledata>
<repetitiongroup>
<dive>
    <date><year>2009</year><month>3</month><day>2</day></date>
    <time><hour>23</hour><minute>2</minute></time>
</dive>
<dive>
    <date><year>2009</year><month>4</month><day>2</day></date>
    <time><hour>23</hour><minute>2</minute></time>
</dive>
<dive>
    <date><year>2009</year><month>4</month><day>2</day></date>
    <time><hour>23</hour><minute>2</minute></time>
</dive>
<dive>
    <date><year>2009</year><month>3</month><day>2</day></date>
    <time><hour>23</hour><minute>2</minute></time>
</dive>
</repetitiongroup>
<repetitiongroup> <!-- one more repetition group which shall be removed -->
<dive>
    <date><year>2009</year><month>3</month><day>2</day></date>
    <time><hour>23</hour><minute>2</minute></time>
</dive>
</repetitiongroup>
</profiledata>
</uddf>
"""))
        compact(tree)
        self.assertEquals(1, len(tree.findall(q('//repetitiongroup'))))
        dives = tree.findall(q('//dive'))
        self.assertEquals(2, len(dives))

        # check the order of dives (ordered by dive time)
        dt = get_time(dives[0])
        self.assertEquals(datetime(2009, 3, 2, 23, 2), dt)

        dt = get_time(dives[1])
        self.assertEquals(datetime(2009, 4, 2, 23, 2), dt)


