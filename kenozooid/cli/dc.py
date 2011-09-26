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

import itertools
import logging

from kenozooid.component import inject
from kenozooid.cli import CLIModule, ArgumentError, add_master_command, \
        _dive_data
from kenozooid.component import query, params
from kenozooid.driver import DeviceDriver, Simulator, DataParser

log = logging.getLogger('kenozooid.cli.dc')

# for commands 'sim plan', 'sim replay'
add_master_command('sim',
        'Kenozooid dive simulation commands',
        'simulate dives with a dive computer')

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
            if len(tuple(query(DataParser, id=id))) > 0:
                caps.append('backup')
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


@inject(CLIModule, name='sim plan')
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
        import kenozooid.simulation as ks
        from kenozooid.driver import Simulator, find_driver

        drv = args.driver[0]
        port = args.port[0]
        spec = args.plan[0]

        sim = find_driver(Simulator, drv, port)

        if sim is None:
            raise ArgumentError('Device driver %s does not support simulation'
                    .format(drv))
        # '0:30,15 3:00,25 9:00,25 10:30,5 13:30,5 14:00,0')
        p = ks.interpolate(ks.parse(spec))
        ks.simulate(sim, p, args.sim_start, args.sim_stop)



@inject(CLIModule, name='sim replay')
class Simulate(object):
    """
    Replay dive profile on a dive computer.
    """
    description = 'replay dive on a dive computer'

    @classmethod
    def add_arguments(self, parser):
        """
        Add dive computer dive replay arguments.
        """
        parser.add_argument('driver',
                nargs=1,
                help='device driver id')
        parser.add_argument('port',
                nargs=1,
                help='device port, i.e. /dev/ttyUSB0, COM1')
        parser.add_argument('input',
                nargs='+',
                metavar='[dives] input',
                help='dives from specified UDDF file (i.e.  1-3,6 is dive'
                    ' 1, 2, 3, and 6 from a file, all by default)')


    def __call__(self, args):
        """
        Execute dive computer dive replay.
        """
        import kenozooid.simulation as ks
        from kenozooid.driver import Simulator, find_driver

        drv = args.driver[0]
        port = args.port[0]
        # fetch dives and profiles from files provided on command line
        dives = itertools.chain(*_dive_data(args.input))

        sim = find_driver(Simulator, drv, port)

        if sim is None:
            raise ArgumentError('Device driver %s does not support simulation'
                    .format(drv))

        for d, p in dives:
            ks.simulate(sim, p)



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
        import kenozooid.dc as kd

        drv_name = args.driver[0]
        port = args.port[0]
        fout = args.output[0]

        kd.backup(drv_name, port, fout)



@inject(CLIModule, name='dive extract')
class DumpExtract(object):
    """
    Extract dive profiles from dive computer dump (binary) data.
    """
    description = 'extract dives from dive computer backup'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive extract command.
        """
        parser.add_argument('input',
                help='UDDF file with dive computer dump data')
        parser.add_argument('output',
                help='output UDDF file')


    def __call__(self, args):
        """
        Execute dive extract command.
        """
        import kenozooid.dc as kd

        fin = args.input
        fout = args.output
        log.debug('extracting dive profiles from {} (saving to {})' \
                .format(fin, fout))
        kd.extract_dives(fin, fout)



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
        import kenozooid.dc as kd

        drv_name = args.driver[0]
        fin = args.input[0]
        fout = args.output[0]

        kd.convert(drv_name, fin, fout)


# vim: sw=4:et:ai
