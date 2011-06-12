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
    description = 'list available dive computer drivers and their capabilities'

    @classmethod
    def add_arguments(self, parser):
        """
        No arguments for drivers listing.
        """


    def __call__(self, args):
        """
        Execute drivers listing command.
        """
        drivers = query(DeviceDriver)
        print('Available drivers:\n')
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

            print('%s (%s): %s' % (id, name, ', '.join(caps)))


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
    description = 'simulate dive with a dive computer'

    @classmethod
    def add_arguments(self, parser):
        """
        Add dive computer dive simulation arguments.
        """
        parser.add_argument('--no-start',
                action='store_false',
                dest='sim_start',
                default=True,
                help='assume simulation is started, don\'t start simulation')
        parser.add_argument('--no-stop',
                action='store_false',
                dest='sim_stop',
                default=True,
                help='don\'t stop simulation, leave dive computer in simulation mode')
        parser.add_argument('driver',
                nargs=1,
                help='device driver id')
        parser.add_argument('port',
                nargs=1,
                help='device port, i.e. /dev/ttyUSB0, COM1')
        parser.add_argument('plan',
                nargs=1,
                help='dive plan')


    def __call__(self, args):
        """
        Execute dive computer dive simulation.
        """
        from kenozooid.simulation import simulate
        from kenozooid.driver import Simulator, find_driver

        drv = args.driver[0]
        port = args.port[0]
        spec = args.plan[0]

        sim = find_driver(Simulator, drv, port)

        if sim is None:
            print('Device driver %s does not support simulation' % drv)
            sys.exit(3)
        simulate(sim, spec, args.sim_start, args.sim_stop) # '0:30,15 3:00,25 9:00,25 10:30,5 13:30,5 14:00,0')



@inject(CLIModule, name='backup')
class Backup(object):
    """
    Command line module for dive computer data backup.
    """
    description = 'backup dive computer data (logbook, settings, etc.)'

    @classmethod
    def add_arguments(self, parser):
        """
        Add arguments for dive computer data backup command.
        """
        parser.add_argument('driver',
                nargs=1,
                help='device driver id')
        parser.add_argument('port',
                nargs=1,
                help='device port, i.e. /dev/ttyUSB0, COM1')
        parser.add_argument('output',
                nargs=1,
                help='UDDF file to contain dive computer backup')


    def __call__(self, args):
        """
        Execute dive computer data backup command.
        """
        from kenozooid.driver import MemoryDump, find_driver
        import kenozooid.logbook as kl

        drv_name = args.driver[0]
        port = args.port[0]
        fout = args.output[0]

        drv = find_driver(MemoryDump, drv_name, port)
        if drv is None:
            print('Device driver %s does not support memory dump' % drv_name)
            sys.exit(3)

        kl.backup(drv, fout)



@inject(CLIModule, name='convert')
class Convert(object):
    """
    Command line module for binary dive computer data conversion.
    """
    description = 'convert binary dive computer data.'

    @classmethod
    def add_arguments(self, parser):
        """
        Add arguments for dive computer data conversion command.
        """
        parser.add_argument('driver',
                nargs=1,
                help='device driver id')
        parser.add_argument('model',
                nargs=1,
                help='dive computer model description')
        parser.add_argument('input',
                nargs=1,
                help='dive computer binary data')
        parser.add_argument('output',
                nargs=1,
                help='UDDF file to contain dive computer backup')


    def __call__(self, args):
        """
        Execute dive computer data conversion command.
        """
        from kenozooid.driver import MemoryDump, find_driver
        import kenozooid.logbook as kl

        drv_name = args.driver[0]
        model = args.model[0]
        fin = args.input[0]
        fout = args.output[0]

        drv = find_driver(MemoryDump, drv_name)
        if drv is None:
            print('Device driver %s does not support memory dump' % drv_name)
            sys.exit(3)

        with open(fin, 'rb') as f:
            data = f.read()
        kl.convert(drv, model, data, fout)


# vim: sw=4:et:ai
