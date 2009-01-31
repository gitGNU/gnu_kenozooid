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
Dummy driver does not communicate to any computer device. Instead, it
provides some sample data and displays provided information like time and
depth during dive simulation.
"""

from datetime import datetime

class DummyDriver(object):
    def id(self):
        return 'Dummy Device'

        

class DummySimulator(object):
    """
    Dummy simulator implementation.
    """
    def __init__(self, driver):
        self.driver = driver


    def start(self):
        """
        Print information about starting dive simulation.
        """
        print 'Starting dive simulation'


    def depth(self, d):
        """
        Print current time and depth.
        """
        print '%s -> %02dm' % (datetime.now().time(), d)


    def stop(self):
        """
        Print information about stopping dive simulation.
        """
        print 'Stopping dive simulation'


