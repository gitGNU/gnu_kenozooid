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
Dummy driver does not communicate to any computer device. Instead, it
provides some sample data and displays provided information like time and
depth during dive simulation.
"""

from datetime import datetime

from kenozooid.driver import DeviceDriver, Simulator
from kenozooid.component import inject

@inject(DeviceDriver, id='dummy', name='Dummy Device Driver',
        models=('Dummy',))
class DummyDriver(object):
    def version(self):
        return 'Dummy Device 1.0'

    @staticmethod
    def scan(port=None):
        yield DummyDriver()

        

@inject(Simulator, id='dummy')
class DummySimulator(object):
    """
    Dummy simulator implementation.
    """
    def start(self):
        """
        Print information about starting dive simulation.
        """
        print('Starting dive simulation')


    def depth(self, d):
        """
        Print current time and depth.
        """
        print('%s -> %02dm' % (datetime.now().time(), d))


    def stop(self):
        """
        Print information about stopping dive simulation.
        """
        print('Stopping dive simulation')


