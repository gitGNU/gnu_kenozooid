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

import sys
import optparse
import itertools
from cStringIO import StringIO

from kenozooid.component import inject
from kenozooid.cli import CLIModule, ArgumentError
from kenozooid.component import query, params
from kenozooid.uddf import node_range



@inject(CLIModule, name='dives')
class ListDives(object):
    """
    List dives from UDDF file.
    """
    usage = '<input> ...'
    description = 'list dives stored in UDDF file'

    def add_options(self, parser):
        """
        Add options for dive list fetched from UDDF file.
        """
        group = optparse.OptionGroup(parser, 'Dive List Options')
        group.add_option('--csv',
                action='store_true',
                dest='dives_csv',
                default=False,
                help='list dives in CSV format')
        parser.add_option_group(group)


    def __call__(self, options, *args):
        """
        Execute command for list of dives in UDDF file.
        """
        from kenozooid.uddf import parse, dive_data, dive_profile
        from kenozooid.util import min2str, FMT_DIVETIME

        if len(args) < 2:
            raise ArgumentError()

        csv = options.dives_csv

        if csv:
            print 'file,number,start_time,time,depth'
        for fin in args[1:]:
            nodes = parse(fin, '//uddf:dive')
            dives = ((dive_data(n), dive_profile(n)) for n in nodes)

            if not csv:
                print fin + ':'
            for i, (d, dp) in enumerate(dives):
                vtime, vdepth, vtemp = zip(*dp)
                depth = max(vdepth)
                if csv:
                    fmt = u'{file},{no},{stime},{dtime},{depth:.1f}'
                    dtime = max(vtime)
                else:
                    fmt = u'{no:4}: {stime}   t={dtime}   \u21a7{depth:.1f}m' 
                    dtime = min2str(max(vtime) / 60.0)
                print fmt.format(no=i + 1,
                        stime=d.time.strftime(FMT_DIVETIME),
                        dtime=dtime,
                        depth=depth,
                        file=fin)



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
    usage = '[dives] <input> ... <output>'
    description = 'plot profiles of dives ([dives] - dive range, i.e. 1-3,6 ' \
        'indicates\n        dive 1, 2, 3 and 6)'

    def add_options(self, parser):
        """
        Add options for plotting profiles of dives command.
        """
        group = optparse.OptionGroup(parser, 'Dive Profile Plotting Options')
        group.add_option('--title',
                action='store_true',
                dest='plot_title',
                default=False,
                help='display plot title')
        group.add_option('--info',
                action='store_true',
                dest='plot_info',
                default=False,
                help='display dive information (depth, time, temperature)')
        group.add_option('--temp',
                action='store_true',
                dest='plot_temp',
                default=False,
                help='plot temperature graph')
        group.add_option('--no-sig',
                action='store_false',
                dest='plot_sig',
                default=True,
                help='do not display Kenozooid signature')
        group.add_option('--no-legend',
                action='store_false',
                dest='plot_legend',
                default=True,
                help='do not display graph legend')
        group.add_option('--overlay',
                action='store_true',
                dest='plot_overlay',
                default=False,
                help='overlay plots in one graph')
        group.add_option('--labels',
                action='store',
                type='string',
                dest='plot_labels',
                help='override dives labels')
        parser.add_option_group(group)


    def __call__(self, options, *args):
        """
        Execute dives' profiles plotting command.
        """
        import os.path
        import itertools
        from kenozooid.plot import plot, plot_overlay
        from kenozooid.uddf import parse, dive_data, dive_profile

        if len(args) < 3:
            raise ArgumentError()

        fout = args[-1]

        _, ext = os.path.splitext(fout)
        ext = ext.replace('.', '')
        if ext.lower() not in ('svg', 'pdf', 'png'):
            print >> sys.stderr, 'Unknown format: %s' % ext
            sys.exit(2)

        args = args[1 : -1]
        def fetch(args):
            i = 0
            while i < len(args):
                q = '//uddf:dive'
                if os.path.exists(args[i]):
                    f = args[i] # no range spec, just filename; take all
                else:
                    q += '[' + node_range(args[i]) + ']'
                    i += 1 # skip range spec
                    f = args[i]
                    if not os.path.exists(f):
                        print >> sys.stderr, 'File does not exist: %s' % f
                        sys.exit(2)

                # return generator of dive data and its profile data tuples
                nodes = parse(f, q)
                yield ((dive_data(n), dive_profile(n)) for n in nodes)
                i += 1

        # fetch dives and profiles from every file
        data = itertools.chain(*fetch(args))
        if options.plot_overlay:
            plotf = plot_overlay

            params = {}
            if options.plot_labels:
                params = { 'labels': options.plot_labels.split(',') }
        else:
            plotf = plot
            params = {}

        plotf(fout, data, format=ext,
            title=options.plot_title,
            info=options.plot_info,
            temp=options.plot_temp,
            sig=options.plot_sig,
            legend=options.plot_legend,
            **params)


# vim: sw=4:et:ai
