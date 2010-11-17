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
UDDF related Kenozooid command line commands.
"""

import optparse
from cStringIO import StringIO

from kenozooid.component import inject
from kenozooid.cli import CLIModule, ArgumentError
from kenozooid.component import query, params


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



@inject(CLIModule, name='dives')
class ListDives(object):
    """
    List dives from UDDF file.
    """
    usage = '<input>'
    description = 'list dives stored in UDDF file'

    def add_options(self, parser):
        """
        No options for UDDF file dive list.
        """


    def __call__(self, options, *args):
        """
        Execute command for list of dives in UDDF file.
        """
        import kenozooid.uddf
        from kenozooid.util import min2str, FMT_DIVETIME

        if len(args) != 2:
            raise ArgumentError()

        fin = args[1]

        pd = kenozooid.uddf.UDDFProfileData()
        pd.open(fin)

        for dive in pd.get_dives():
            #print u'%02d,%s,%s,%.2f' \
            #    % (dive[0], dive[1].strftime(FMT_DIVETIME), dive[2], dive[3])
            print u'%02d: %s   t=%s   \u21a7%.2fm' \
                % (dive[0], dive[1].strftime(FMT_DIVETIME), min2str(dive[2]), dive[3])



@inject(CLIModule, name='convert')
class ConvertFile(object):
    """
    Convert UDDF dive memory dumps into UDDF dive profiles.
    """
    usage = '<dump1> [dump2 ...] <output>'
    description = 'convert UDDF dive memory dumps into UDDF dive profiles'

    def add_options(self, parser):
        """
        No options file conversion command.
        """


    def __call__(self, options, *args):
        """
        Execute file conversion command.
        """
        from kenozooid.driver import MemoryDump, find_driver
        import kenozooid.uddf

        if len(args) < 3:
            raise ArgumentError()

        fin = args[1:-1]
        fout = args[-1]

        # create uddf file with profile data
        pd = kenozooid.uddf.UDDFProfileData()
        pd.create()

        for fn in fin:
            # read uddf file containing device dump
            dd = kenozooid.uddf.UDDFDeviceDump()
            dd.open(fn)

            drv = dd.get_model_id()
            model = dd.get_model()
            data = dd.get_data()

            pd.set_model(drv, model)

            dumper = find_driver(MemoryDump, drv, None)
            dumper.convert(dd.tree, StringIO(data), pd.tree)

        pd.save(fout)



@inject(CLIModule, name='plot')
class PlotProfiles(object):
    """
    Plot profiles of dives command.
    """
    usage = '<input> [dives] <prefix> <format>'
    description = 'plot profiles of dives ([dives] - dive range, i.e. 1-3,6 ' \
        'indicates\n        dive 1, 2, 3 and 6)'

    def add_options(self, parser):
        """
        Add options for plotting profiles of dives command.
        """
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


    def __call__(self, options, *args):
        """
        Execute dives' profiles plotting command.
        """
        import kenozooid.plot
        import kenozooid.uddf

        if len(args) != 4 and len(args) != 5:
            raise ArgumentError()

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


# vim: sw=4:et:ai
