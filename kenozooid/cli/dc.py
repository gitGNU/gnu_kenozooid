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
Dive computer related Kenozooid command line commands.
"""

import optparse

from kenozooid.component import inject
from kenozooid.cli import CLIModule, ArgumentError
from kenozooid.component import query, params
from kenozooid.driver import DeviceDriver, Simulator, MemoryDump


@inject(CLIModule, name='drivers')
class ListDrivers(object):
    """
    Dive computers drivers listing command line module.
    """
    usage = ''
    description = 'list available dive computer drivers and their capabilities'

    def add_options(self, parser):
        """
        No options for drivers listing.
        """


    def __call__(self, options, *args):
        """
        Execute drivers listing command.
        """
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


### def cmd_scan(parser, options, args):
###     from kenozooid.component import query, params
###     from kenozooid.driver import DeviceDriver, DeviceError
### 
###     print 'Scanning...\n'
###     for cls in query(DeviceDriver):
###         for drv in cls.scan():
###             p = params(cls)
###             id = p['id']
###             name = p['name']
###             try:
###                 print 'Found %s (%s): %s' % (id, name, drv.version())
###             except DeviceError, ex:
###                 print >> sys.stderr, 'Device %s (%s) error: %s' % (id, name, ex)


@inject(CLIModule, name='simulate')
class Simulate(object):
    """
    Simulate dive on a dive computer.
    """
    usage = '<drv> <port> <dive plan>'
    description = 'simulate dive with a dive computer'

    def add_options(self, parser):
        """
        Add dive computer dive simulation options.
        """
        group = optparse.OptionGroup(parser, 'Dive Simulation Options')
        group.add_option('--no-start',
                action='store_false',
                dest='sim_start',
                default=True,
                help='assume simulation is started, don\'t start simulation')
        group.add_option('--no-stop',
                action='store_false',
                dest='sim_stop',
                default=True,
                help='don\'t stop simulation, leave dive computer in simulation mode')
        parser.add_option_group(group)


    def __call__(self, options, *args):
        """
        Execute dive computer dive simulation.
        """
        from kenozooid.simulation import simulate
        from kenozooid.driver import Simulator, find_driver

        if len(args) != 4:
            raise ArgumentError()

        drv = args[1]
        port = args[2]
        spec = args[3]

        sim = find_driver(Simulator, drv, port)

        if sim is None:
            print 'Device driver %s does not support simulation' % drv
            sys.exit(3)
        simulate(sim, spec, options.sim_start, options.sim_stop) # '0:30,15 3:00,25 9:00,25 10:30,5 13:30,5 14:00,0')



@inject(CLIModule, name='dump')
class Dump(object):
    """
    Command module for dive computer memory dumping.
    """
    usage = '<drv> <port> <output>'
    description = 'dump dive computer memory (logbook, settings, etc.)'

    def add_options(self, parser):
        """
        No options for dive computer memory dumping.
        """


    def __call__(self, options, *args):
        """
        Execute dive computer memory dump command.
        """
        from kenozooid.driver import MemoryDump, find_driver
        import kenozooid.uddf

        if len(args) != 4:
            raise ArgumentError()

        drv = args[1]
        port = args[2]
        fout = args[3]

        dumper = find_driver(MemoryDump, drv, port)
        if dumper is None:
            print 'Device driver %s does not support memory dump' % drv
            sys.exit(3)

        data = dumper.dump()
        dd = kenozooid.uddf.UDDFDeviceDump()
        dd.create()
        dd.set_model(drv, DRIVERS[drv])
        dd.set_data(dumper.dump())
        dd.save(fout)


# vim: sw=4:et:ai
