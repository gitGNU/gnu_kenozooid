#
# Kenozooid - software stack to support OSTC dive computer.
#
# Copyright (C) 2009 by wrobell <wrobell@pld-linux.org>
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
Test interface injection mechanism.
"""

import unittest

from kenozooid.iface import _registry, inject, query, DeviceDriver


class TestCase(unittest.TestCase):
    def tearDown(self):
        """
        Clear interface registry after each test.
        """
        _registry.clear()



class InjectionTestCase(TestCase):
    """
    Interface injection tests.
    """
    def test_single_injection(self):
        """Test interface injection
        """
        @inject(DeviceDriver, 'test')
        class C(object): pass

        self.assertTrue(DeviceDriver in _registry)
        self.assertTrue('test' in _registry[DeviceDriver])
        self.assertEquals(C, _registry[DeviceDriver]['test'])


    def test_multiple_injection(self):
        """Test interface injection with multiple classes
        """
        @inject(DeviceDriver, 'test1')
        class C1(object): pass

        @inject(DeviceDriver, 'test2')
        class C2(object): pass

        self.assertTrue(DeviceDriver in _registry)
        self.assertTrue('test1' in _registry[DeviceDriver])
        self.assertEquals(C1, _registry[DeviceDriver]['test1'])

        self.assertTrue('test2' in _registry[DeviceDriver])
        self.assertEquals(C2, _registry[DeviceDriver]['test2'])



class QueryTestCase(TestCase):
    """
    Interface registry query tests.
    """
    def test_query(self):
        """Test interface registry query
        """
        @inject(DeviceDriver, 'test')
        class C(object): pass

        result = query(DeviceDriver)
        self.assertEquals((C, ), result)


    def test_multiple_query(self):
        """Test interface registry query with multiple injections
        """
        @inject(DeviceDriver, 'test1')
        class C1(object): pass

        @inject(DeviceDriver, 'test2')
        class C2(object): pass

        result = query(DeviceDriver)
        self.assertEquals((C1, C2), tuple(sorted(result)))
