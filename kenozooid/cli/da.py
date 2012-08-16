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
Kenozooid's plotting and data analysis command line user interface.
"""

import os.path
import logging

from kenozooid.component import inject
from kenozooid.cli import CLIModule, ArgumentError, add_master_command, \
        add_uddf_input

log = logging.getLogger('kenozooid.cli.da')

@inject(CLIModule, name='plot')
class PlotProfiles(object):
    """
    Plot profiles of dives command.
    """
    description = 'plot graphs of dive profiles'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for plotting profiles of dives command.
        """
        parser.add_argument('--type', '-t',
                dest='plot_type',
                default='details',
                choices=('details', 'cmp'),
                help='type of plot')
        parser.add_argument('--title',
                action='store_true',
                dest='plot_title',
                default=False,
                help='display plot title')
        parser.add_argument('--info',
                action='store_true',
                dest='plot_info',
                default=False,
                help='display dive information (depth, time, temperature)')
        parser.add_argument('--avg-depth',
                action='store_true',
                dest='plot_avg_depth',
                default=False,
                help='display dive average depth')
        parser.add_argument('--mod',
                action='store_true',
                dest='plot_mod',
                default=False,
                help='plot MOD of current gas (for 1.4 and 1.6 ppO2)')
        parser.add_argument('--temp',
                action='store_true',
                dest='plot_temp',
                default=False,
                help='plot temperature graph')
        parser.add_argument('--no-sig',
                action='store_false',
                dest='plot_sig',
                default=True,
                help='do not display Kenozooid signature')
        parser.add_argument('--legend',
                action='store_true',
                dest='plot_legend',
                default=False,
                help='display graph legend')
        parser.add_argument('--labels',
                nargs='*',
                action='store',
                dest='plot_labels',
                help='override dives labels')
        add_uddf_input(parser)
        parser.add_argument('output',
                help='output file: pdf, png or svg')


    def __call__(self, args):
        """
        Execute dives' profiles plotting command.
        """
        import os.path
        import kenozooid.plot as kp
        import kenozooid.logbook as kl

        fout = args.output

        _, ext = os.path.splitext(fout)
        ext = ext.replace('.', '')
        if ext.lower() not in ('pdf', 'png', 'svg'):
            raise ArgumentError('Unknown format of plotting output file: {0}' \
                    .format(ext))

        r, f = args.input
        dives = kl.find_dives(f, r, args.dives)

        kp.plot(dives, fout,
            ptype=args.plot_type,
            format=ext,
            title=args.plot_title,
            info=args.plot_info,
            temp=args.plot_temp,
            avg_depth=args.plot_avg_depth,
            mod=args.plot_mod,
            sig=args.plot_sig,
            legend=args.plot_legend,
            labels=args.plot_labels)



@inject(CLIModule, name='analyze')
class Analyze(object):
    """
    Analyze dives with R script.
    """
    description = 'analyze dives with R script'

    @classmethod
    def add_arguments(self, parser):
        """
        Add R script runner options.
        """
        parser.add_argument('script', help='R script to execute')
        parser.add_argument('-a',
                nargs='*',
                dest='args',
                help='R script arguments')
        add_uddf_input(parser)


    def __call__(self, args):
        """
        Execute dives' analyze command.
        """
        from kenozooid.analyze import analyze
        import kenozooid.logbook as kl

        r, f = args.input
        dives = kl.find_dives(f, r, args.dives)
        analyze(args.script, args.args, dives)


# vim: sw=4:et:ai

