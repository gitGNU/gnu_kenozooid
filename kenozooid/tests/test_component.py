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
Test component interface injection mechanism and component repository.
"""

import unittest

from kenozooid.driver import DeviceDriver
from kenozooid.component import _registry, _applies, inject, query


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
        @inject(DeviceDriver, id='test', name='Test')
        class C(object): pass

        self.assertTrue(DeviceDriver in _registry)
        p = {'id': 'test', 'name': 'Test'}
        self.assertTrue((C, p) in _registry[DeviceDriver])


    def test_multiple_injection(self):
        """Test interface injection with multiple classes
        """
        @inject(DeviceDriver, id='test1', name='Test1')
        class C1(object): pass

        @inject(DeviceDriver, id='test2', name='Test2')
        class C2(object): pass

        self.assertTrue(DeviceDriver in _registry)
        p = {'id': 'test1', 'name': 'Test1'}
        self.assertTrue((C1, p) in _registry[DeviceDriver])

        p = {'id': 'test2', 'name': 'Test2'}
        self.assertTrue((C2, p) in _registry[DeviceDriver])



class QueryTestCase(TestCase):
    """
    Interface registry query tests.
    """
    def test_dict_cmp(self):
        p1 = {3: 4}
        p2 = {1: 2, 3: 4}

        self.assertTrue(_applies(p1, p2))

        p1 = {3: 3}
        self.assertFalse(_applies(p1, p2))

        p1 = {4: 3}
        self.assertFalse(_applies(p1, p2))


    def test_cls_query(self):
        """Test interface registry query
        """
        @inject(DeviceDriver, id='test', name='Test')
        class C(object): pass

        result = query(DeviceDriver)
        self.assertEquals((C, ), tuple(result))


    def test_cls_multiple_query(self):
        """Test interface registry query with multiple injections
        """
        @inject(DeviceDriver, id='test1', name='Test1')
        class C1(object): pass

        @inject(DeviceDriver, id='test2', name='Test2')
        class C2(object): pass

        result = tuple(query(DeviceDriver))
        self.assertEquals(2, len(result))
        self.assertTrue(C1 in result, result)
        self.assertTrue(C2 in result, result)


    def test_parameter_query(self):
        """Test parameter query
        """
        @inject(DeviceDriver, id='test1', name='Test1')
        class C1(object): pass

        @inject(DeviceDriver, id='test2', name='Test2a')
        class C2(object): pass

        @inject(DeviceDriver, id='test2', name='Test2b')
        class C3(object): pass

        result = tuple(query(id='test1'))
        self.assertEquals(1, len(result))
        self.assertEquals(C1, result[0])

        result = tuple(query(id='test2'))
        self.assertEquals(2, len(result))
        self.assertTrue(C2 in result)
        self.assertTrue(C3 in result)
