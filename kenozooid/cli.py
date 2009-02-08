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
Commmand line user interface.
"""

import logging
import sys

from kenozooid.component import query, params
from kenozooid.simulation import simulate
from kenozooid.driver import DeviceDriver, Simulator, DeviceError


def cmd_list(parser, options, args):
    drivers = query(DeviceDriver)
    print 'Available drivers:\n'
    for cls in drivers:
        p = params(cls)
        id = p['id']
        name = p['name']
        drivers = query(id=id)

        # find capabilities
        caps = []
        if len(tuple(query(Simulator, id=id))) > 0:
            caps.append('simulation')
        #if len(tuple(query(DiveLog, id=id))) > 0:
        #    caps.append('divelog')
        # ... etc ...

        print '%s (%s): %s' % (id, name, ', '.join(caps))


def cmd_scan(parser, options, args):
    print 'Scanning...\n'
    for cls in query(DeviceDriver):
        for drv in cls.scan():
            p = params(cls)
            id = p['id']
            name = p['name']
            try:
                print 'Found %s (%s): %s' % (id, name, drv.version())
            except DeviceError, ex:
                print >> sys.stderr, 'Device %s (%s) error: %s' % (id, name, ex)


def cmd_simulate(parser, options, args):
    if len(args) != 3:
        parser.print_help()
        sys.exit(2)

    id = args[1]
    spec = args[2]

    try:
        cls = query(DeviceDriver, id=id).next()
    except StopIteration, ex:
        print 'Cannot find device driver for id %s' % id
        sys.exit(3)

    try:
        drv = cls.scan().next()
    except StopIteration, ex:
        print 'Device with id %s seems to be not connected' % id
        sys.exit(3)

    try:
        cls = query(Simulator, id=id).next()
        sim = cls(drv)
    except StopIteration, ex:
        print 'Device driver %s does not support simulation' % id
        sys.exit(3)

    simulate(sim, spec) # '0:30,15 3:00,25 9:00,25 10:30,5 13:30,5 14:00,0')


# map cli command names to command functions
COMMANDS = {
    'list': cmd_list,
    'scan': cmd_scan,
    'simulate': cmd_simulate,
}

