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
import lxml.etree as et

from kenozooid.component import query, params
from kenozooid.simulation import simulate
from kenozooid.driver import DeviceDriver, Simulator, MemoryDump, \
    DeviceError, find_driver
from kenozooid.util import save
import kenozooid.uddf
import kenozooid.plot


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
        if len(tuple(query(MemoryDump, id=id))) > 0:
            caps.append('dump')
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

    sim = find_driver(Simulator, id)

    if sim is None:
        print 'Device driver %s does not support simulation' % id
        sys.exit(3)
    simulate(sim, spec, options.sim_start, options.sim_stop) # '0:30,15 3:00,25 9:00,25 10:30,5 13:30,5 14:00,0')


def cmd_dump(parser, options, args):
    """
    Implementation fo memory dump command. 
    """
    if len(args) != 3:
        parser.print_help()
        sys.exit(2)

    id = args[1]
    filename = args[2]

    dumper = find_driver(MemoryDump, id)
    if dumper is None:
        print 'Device driver %s does not support memory dump' % id

    saved = save(filename, dumper.dump())
    if not saved:
        print 'File %s already exists' % filename


def cmd_convert(parser, options, args):
    """
    Implementation of file conversion command. The command handles all
    supported data formats like dive computer memory dumps and UDDF.
    """
    if len(args) != 3:
        parser.print_help()
        sys.exit(2)

    # create uddf file
    tree = kenozooid.uddf.create()

    # convert ostc dump to uddf (so far only ostc dump is supported, in the
    # future dump format detection and converter finding need to happen
    # here)
    cls = query(MemoryDump, id='ostc').next()
    dumper = cls()
    with open(args[1]) as f:
        dumper.convert(f, tree)
    kenozooid.uddf.validate(tree)

    with open(args[2], 'w') as f:
        data = et.tostring(tree, pretty_print=True)
        f.write(data)


def cmd_plot(parser, options, args):
    """
    Implementation of dive profile plotting command.
    """
    if len(args) != 3:
        parser.print_help()
        sys.exit(2)

    fin = args[1]
    fout = args[2]

    kenozooid.plot.plot(fin, fout, options.plot_title, options.plot_info,
            options.plot_temp)


# map cli command names to command functions
COMMANDS = {
    'list': cmd_list,
    'scan': cmd_scan,
    'simulate': cmd_simulate,
    'dump': cmd_dump,
    'convert': cmd_convert,
    'plot': cmd_plot,
}

