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

import optparse
import logging
import sys
import lxml.etree as et
import lxml.objectify as eto
from cStringIO import StringIO

class RangeError(ValueError): pass

def parse_range(s, infinity=100):
    """
    Parse textual representation of number range.

    Example of a range

    >>> parse_range('1-3,5')
    (1, 2, 3, 5)

    Example of infinite range

    >>> parse_range('20-') # doctest:+ELLIPSIS
    (20, 21, 22, ..., 99, 100)

    :Parameters:
     s
        Textual representation of number range.
     infinity
        Maximum value when infinite range is specified.
    """
    def toint(d):
        try:
            return int(d)
        except ValueError, ex:
            raise RangeError('Invalid range %s' % s)

    data = []
    for r in s.split(','):
        d = r.split('-')
        if len(d) == 1:
            data.append(toint(d[0]))
        elif len(d) == 2:
            a = toint(d[0])
            b = infinity if d[1].strip() == '' else toint(d[1])
            data.extend(range(a, b + 1))
        else:
            raise RangeError('Invalid range %s' % s)
    return tuple(data)


def cmd_list(parser, options, args):
    from kenozooid.component import query, params
    from kenozooid.driver import DeviceDriver, Simulator, MemoryDump

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
    from kenozooid.component import query, params
    from kenozooid.driver import DeviceDriver, DeviceError

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
    from kenozooid.simulation import simulate
    from kenozooid.driver import Simulator, find_driver

    if len(args) != 4:
        parser.print_help()
        sys.exit(2)

    drv = args[1]
    port = args[2]
    spec = args[3]

    sim = find_driver(Simulator, drv, port)

    if sim is None:
        print 'Device driver %s does not support simulation' % drv
        sys.exit(3)
    simulate(sim, spec, options.sim_start, options.sim_stop) # '0:30,15 3:00,25 9:00,25 10:30,5 13:30,5 14:00,0')


def cmd_dump(parser, options, args):
    """
    Implementation fo memory dump command. 
    """
    from kenozooid.driver import MemoryDump, find_driver
    import kenozooid.uddf

    if len(args) != 4:
        parser.print_help()
        sys.exit(2)

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
    dd.set_id(drv)
    dd.set_data(dumper.dump())
    dd.save(fout)


def cmd_dives(parser, options, args):
    """
    Implementation of dive listing command.
    """
    import kenozooid.uddf
    from kenozooid.util import min2str

    if len(args) != 2:
        parser.print_help()
        sys.exit(2)

    fin = args[1]

    pd = kenozooid.uddf.UDDFProfileData()
    pd.open(fin)

    for dive in pd.get_dives(fin):
        print u'%02d: %s   t=%s   \u21a7%.2fm' \
            % (dive[0], dive[1], min2str(dive[2]), dive[3])


def cmd_convert(parser, options, args):
    """
    Implementation of file conversion command. The command handles all
    supported data formats like dive computer memory dumps and UDDF.
    """
    from kenozooid.driver import MemoryDump, find_driver
    import kenozooid.uddf

    if len(args) < 3:
        parser.print_help()
        sys.exit(2)

    fin = args[1:-1]
    fout = args[-1]

    # create uddf file with profile data
    pd = kenozooid.uddf.UDDFProfileData()
    pd.create()

    for fn in fin:
        # read uddf file containing device dump
        dd = kenozooid.uddf.UDDFDeviceDump()
        dd.open(fn)
        drv = dd.get_id()
        data = dd.get_data()

        dumper = find_driver(MemoryDump, drv, None)
        dumper.convert(dd.tree, StringIO(data), pd.tree)

    pd.save(fout)


def cmd_plot(parser, options, args):
    """
    Implementation of dive profile plotting command.
    """
    import kenozooid.plot
    import kenozooid.uddf

    if len(args) != 4 and len(args) != 5:
        parser.print_help()
        sys.exit(2)

    if len(args) == 4:
        fin = args[1]
        fprefix = args[2]
        format = args[3]
        dives = None
    else:
        fin = args[1]
        dives = parse_range(args[2])
        fprefix = args[3]
        format = args[4]

    if format.lower() not in ('svg', 'pdf', 'png'):
        print >> sys.stderr, 'Unknown format: %s' % format
        sys.exit(2)

    pd = kenozooid.uddf.UDDFProfileData()
    pd.open(fin)
    kenozooid.plot.plot(pd.tree, fprefix, format,
            dives=dives,
            title=options.plot_title,
            info=options.plot_info,
            temp=options.plot_temp)


def main():
    usage = """
        %prog [options] list
        %prog [options] simulate <drv> <port> <dive plan>
        %prog [options] dump <drv> <port> <output>
        %prog [options] dives <input>
        %prog [options] convert <dump1> [dump2 ...] <output>
        %prog [options] plot <input> [dives] <prefix> <format>

    Commands Description:
        list - list available drivers and their capabilities
        simulate - simulate dive
        dump - dump dive computer memory (logbook, settings, etc.)
        dives - list dives stored in a file
        convert - convert dive computer memory dumps into UDDF format
        plot - plot profiles of dives (all by default) into files
               named <prefix>-<no>.<format>' (no is number of a dive from input
               file, and format is one of pdf, svg or png)
               
        [dives] - dive range, i.e. 1-3,6 indicates dive 1, 2, 3 and 6
    """

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-v', '--verbose',
            action='store_true', dest='verbose', default=False,
            help='explain what is being done')
    parser.add_option('--profile',
            action='store_true', dest='profile', default=False,
            help='run with profiler')

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

    group = optparse.OptionGroup(parser, 'Dive Profile Plotting Options')
    group.add_option('--no-title',
            action='store_false',
            dest='plot_title',
            default=True,
            help='don\'t display plot title')
    group.add_option('--no-info',
            action='store_false',
            dest='plot_info',
            default=True,
            help='don\'t display dive information (depth, time, temperature)')
    group.add_option('--no-temp',
            action='store_false',
            dest='plot_temp',
            default=True,
            help='don\'t plot temperature graph')
    parser.add_option_group(group)

    options, args = parser.parse_args()

    # configure basic logger
    logging.basicConfig()
    logging.Logger.manager.loggerDict.clear()
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    if options.verbose:
        logging.root.setLevel(logging.DEBUG)

    # don't import kenozooid modules until logger is configured

    # import modules implementing supported drivers
    # todo: support dynamic import of third party drivers
    from kenozooid.driver import DeviceError
    import kenozooid.driver.dummy
    import kenozooid.driver.ostc
    import kenozooid.driver.su

    if len(args) < 1 or args[0] not in COMMANDS:
        parser.print_help()
        sys.exit(1)

    cmd = args[0]
    assert cmd in COMMANDS

    f = COMMANDS[cmd]
    try:
        if options.profile:
            import hotshot, hotshot.stats
            prof = hotshot.Profile('kenozooid.prof')
            prof.runcall(f, parser, options, args)
            prof.close()
            stats = hotshot.stats.load('kenozooid.prof')
            stats.strip_dirs()
            stats.sort_stats('time', 'calls')
            stats.print_stats(20)
        else:
            f(parser, options, args)
    except DeviceError, ex:
        print ex


# map cli command names to command functions
COMMANDS = {
    'list': cmd_list,
#    'scan': cmd_scan,
    'simulate': cmd_simulate,
    'dump': cmd_dump,
    'dives': cmd_dives,
    'convert': cmd_convert,
    'plot': cmd_plot,
}

