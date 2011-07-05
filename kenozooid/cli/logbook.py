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
Kenozooid's logbook command line user interface.
"""

import sys
import itertools
import os
import os.path
from functools import partial
from lxml import etree as et
import logging

from kenozooid.component import inject
from kenozooid.cli import CLIModule, ArgumentError, add_master_command
from kenozooid.component import query, params
from kenozooid.uddf import node_range
from kenozooid.util import nformat

log = logging.getLogger('kenozooid.cli.uddf')


# for commands 'dive add', 'dive list', etc
add_master_command('dive',
        'Kenozooid dive management commands',
        'manage dives in UDDF file')

# for commands 'site add', 'site list', etc
add_master_command('site',
        'Kenozooid dive site management commands',
        'manage dive sites in UDDF file')

# for commands 'buddy add', 'buddy list', etc
add_master_command('buddy',
        'Kenozooid dive buddy management commands',
        'manage dive buddies in UDDF file')


@inject(CLIModule, name='dive list')
class ListDives(object):
    """
    List dives from UDDF file.
    """
    description = 'list dives stored in UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive list fetched from UDDF file.
        """
        parser.add_argument('input',
                nargs='+',
                help='UDDF file with dive profiles')


    def __call__(self, args):
        """
        Execute command for list of dives in UDDF file.
        """
        import kenozooid.logbook as kl

        csv = args.dives_csv
        files = args.input

        for fin in files:
            print('{}:'.format(fin))
            for i, dl in enumerate(kl.list_dives(fin), 1):
                l =  ' '.join('{:>9}'.format(s) for s in dl)
                print('{:5}: {}'.format(i, l))



@inject(CLIModule, name='dive add')
class AddDive(object):
    """
    Add a dive to UDDF file.
    """
    description = 'add dive to UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive adding to UDDF file.
        """
        g = parser.add_mutually_exclusive_group(required=True)
        g.add_argument('-d', '--with-depth',
                nargs=3,
                metavar=('time', 'depth', 'duration'),
                help='add dive with dive time, maximum depth and dive'
                    ' duration data')
        g.add_argument('-p', '--with-profile',
                nargs=2,
                metavar=('dive', 'input'),
                help='add dive data with profile data from an UDDF file')

        parser.add_argument('-s', '--site', metavar='site',
                help='dive site')
        parser.add_argument('-b', '--buddy', metavar='buddy',
                help='dive buddy')
        parser.add_argument('output', nargs=1, help='UDDF output file')


    def __call__(self, args):
        """
        Execute command for adding dives into UDDF file.
        """
        import kenozooid.logbook as kl
        from dateutil.parser import parse as dparse
        from copy import deepcopy

        time, depth, duration = None, None, None
        dive_no, fin = None, None

        fout = args.output[0]

        if args.with_depth:
            try:
                time = dparse(args.with_depth[0])
                depth = float(args.with_depth[1])
                duration = float(args.with_depth[2])
            except ValueError:
                raise ArgumentError('Invalid time, depth or duration parameter')
        else:
            dive_no, fin = args.with_profile
            dive_no = int(no)

        kl.add_dive(fout, time, depth, duration, dive_no, fin)



@inject(CLIModule, name='site add')
class AddDiveSite(object):
    """
    Add dive site to UDDF file.
    """
    description = 'add dive site to UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive site adding to UDDF file.
        """
        parser.add_argument('-p', '--position',
                nargs=2,
                metavar=('x', 'y'),
                type=float,
                help='longitude and latitude of dive site')
        #parser.add_argument('-c', '--country',
        #        nargs=1,
        #        metavar='country',
        #        help='dive site country, i.e. Ireland')
        #parser.add_argument('-p', '--province',
        #        nargs=1,
        #        metavar='province',
        #        help='dive site province, i.e. Howth')
        parser.add_argument('id',
                nargs='?',
                help='id of dive site')
        parser.add_argument('location',
                nargs=1,
                help='location of dive site, i.e. Scapa Flow, Red Sea')
        parser.add_argument('name',
                nargs=1,
                help='name of dive site, i.e. SMS Markgraf, SS Thistlegorm')
        parser.add_argument('output',
                nargs=1,
                help='UDDF output file')


    def __call__(self, args):
        """
        Execute command for adding dive site into UDDF file.
        """
        import kenozooid.uddf as ku

        id = args.id
        if args.position:
            x, y = args.position
        else:
            x, y = None, None
        location = args.location[0]
        name = args.name[0]
        fout = args.output[0]

        if os.path.exists(fout):
            doc = et.parse(fout).getroot()
        else:
            doc = ku.create()

        ku.create_site_data(doc, id=id, location=location, name=name, x=x, y=y)
        ku.save(doc, fout)



@inject(CLIModule, name='site list')
class ListDiveSites(object):
    """
    List dive sites from UDDF file.
    """
    description = 'list dive sites stored in UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive site list fetched from UDDF file.
        """
        parser.add_argument('site',
                nargs='?',
                help='dive site search string; matches id or partially dive' \
                    ' site name')
        parser.add_argument('input',
                nargs='+',
                help='UDDF file with dive sites')


    def __call__(self, args):
        """
        Execute command for list of dive sites in UDDF file.
        """
        import kenozooid.uddf as ku

        fmt = '{0:4} {1.id:10} {1.name:12} {1.location:20}'

        if args.site:
            query = ku.XP_FIND_SITE
        else:
            query = '//uddf:site'
        files = args.input

        for fin in files:
            nodes = ku.parse(fin, query, site=args.site)
            for i, n in enumerate(nodes):
                n = ku.site_data(n)
                print(nformat(fmt, i + 1, n))



@inject(CLIModule, name='site del')
class DelDiveSite(object):
    """
    Remove dive site from UDDF file.
    """
    description = 'remove dive site stored in UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for removal of dive site from UDDF file.
        """
        parser.add_argument('site',
                nargs=1,
                help='dive site search string; matches id or partially dive' \
                    ' site name')
        parser.add_argument('input',
                nargs=1,
                help='UDDF file with dive sites')


    def __call__(self, args):
        """
        Execute command for removal of dive sites from UDDF file.
        """
        import kenozooid.uddf as ku

        query = ku.XP_FIND_SITE
        fin = args.input[0]
        fbk = '{}.bak'.format(fin)

        doc = et.parse(fin)
        ku.remove_nodes(doc, query, site=args.site[0])
        os.rename(fin, fbk)
        try:
            ku.save(doc.getroot(), fin)
        except Exception as ex:
            os.rename(fbk, fin)
            raise ex



@inject(CLIModule, name='buddy add')
class AddBuddy(object):
    """
    Add dive buddy to UDDF file.
    """
    description = 'add dive buddy to UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive buddy adding to UDDF file.
        """
        parser.add_argument('-m', '--member',
                nargs=2,
                metavar=('org', 'number'),
                help='organization and its member id number i.e. CFT 123')
        parser.add_argument('id',
                nargs='?',
                help='id of a buddy, i.e. tcora')
        parser.add_argument('name',
                nargs=1,
                help='buddy name, i.e. "Tom Cora", "Thomas Henry Corra"'
                    ' or "Corra, Thomas Henry"')
        parser.add_argument('output',
                nargs=1,
                help='UDDF output file')


    def __call__(self, args):
        """
        Execute command for adding dive buddy into UDDF file.
        """
        import kenozooid.uddf as ku

        if args.member:
            org, number = args.member
        else:
            org, number = None, None

        id = args.id
        fn, mn, ln = _name_parse(args.name[0])
        fout = args.output[0]

        if os.path.exists(fout):
            doc = et.parse(fout).getroot()
        else:
            doc = ku.create()

        ku.create_buddy_data(doc, id=id, fname=fn, mname=mn,
                lname=ln, org=org, number=number)

        ku.save(doc, fout)


@inject(CLIModule, name='buddy list')
class ListBuddies(object):
    """
    List dive buddies from UDDF file.
    """
    description = 'list dive buddies stored in UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive buddy list fetched from UDDF file.
        """
        parser.add_argument('buddy',
                nargs='?',
                help='buddy search string; matches id, member number or'
                ' partially firstname or lastname')
        parser.add_argument('input',
                nargs='+',
                help='UDDF file with dive buddies')


    def __call__(self, args):
        """
        Execute command for list of dive buddies in UDDF file.
        """
        import kenozooid.uddf as ku

        fmt = '{0:4} {1.id:10} {1.fname:10} {1.lname:20}' \
                ' {1.org:5} {1.number:11}'

        if args.buddy:
            query = ku.XP_FIND_BUDDY
        else:
            query = '//uddf:buddy'
        files = args.input

        for fin in files:
            nodes = ku.parse(fin, query, buddy=args.buddy)
            for i, n in enumerate(nodes):
                b = ku.buddy_data(n)
                print(nformat(fmt, i + 1, b))


@inject(CLIModule, name='buddy del')
class DelBuddy(object):
    """
    Remove dive buddies from UDDF file.
    """
    description = 'remove dive buddies stored in UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for removal of dive buddy from UDDF file.
        """
        parser.add_argument('buddy',
                nargs=1,
                help='buddy search string; matches id, member number or'
                ' partially firstname or lastname')
        parser.add_argument('input',
                nargs=1,
                help='UDDF file with dive buddies')


    def __call__(self, args):
        """
        Execute command for removal of dive buddies from UDDF file.
        """
        import kenozooid.uddf as ku

        query = ku.XP_FIND_BUDDY
        fin = args.input[0]
        fbk = '{}.bak'.format(fin)

        doc = et.parse(fin)
        ku.remove_nodes(doc, query, buddy=args.buddy[0])
        os.rename(fin, fbk)
        try:
            ku.save(doc.getroot(), fin)
        except Exception as ex:
            os.rename(fbk, fin)
            raise ex



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
        parser.add_argument('--overlay',
                action='store_true',
                dest='plot_overlay',
                default=False,
                help='overlay plots in one graph')
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
                action='store',
                dest='plot_labels',
                help='override dives labels')
        parser.add_argument('input',
                nargs='+',
                metavar='[dives] input',
                help='dives from specified UDDF file (i.e.  1-3,6 is dive'
                    ' 1, 2, 3, and 6 from a file, all by default)')
        parser.add_argument('output',
                nargs=1,
                help='output file: pdf, png or svg')


    def __call__(self, args):
        """
        Execute dives' profiles plotting command.
        """
        import os.path
        from kenozooid.plot import plot, plot_overlay

        fout = args.output[0]

        _, ext = os.path.splitext(fout)
        ext = ext.replace('.', '')
        if ext.lower() not in ('pdf', 'png', 'svg'):
            raise ArgumentError('Unknown format: {0}'.format(ext))

        # fetch dives and profiles from files provided on command line
        data = itertools.chain(*_fetch(args.input))
        if args.plot_overlay:
            plotf = plot_overlay

            params = {}
            if args.plot_labels:
                labels = [l.strip() for l in args.plot_labels.split(',')]
                params = { 'labels': labels }
        else:
            plotf = plot
            params = {}

        plotf(fout, data, format=ext,
            title=args.plot_title,
            info=args.plot_info,
            temp=args.plot_temp,
            sig=args.plot_sig,
            legend=args.plot_legend,
            **params)



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
        parser.add_argument('script', nargs=1, help='R script to execute')
        parser.add_argument('-a',
                action='append',
                dest='args',
                help='R script arguments')
        parser.add_argument('input',
                nargs='+',
                metavar='[dives] input',
                help='dives from specified UDDF file (i.e.  1-3,6 is dive'
                    ' 1, 2, 3, and 6 from a file, all by default)')


    def __call__(self, args):
        """
        Execute dives' analyze command.
        """
        from kenozooid.analyze import analyze

        # fetch dives and profiles from files provided on command line
        data = itertools.chain(*_fetch(args.input))
        analyze(args.script[0], data, args.args)



def _fetch(args):
    from kenozooid.uddf import parse, dive_data, dive_profile
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
                raise ArgumentError('File does not exist: {0}'.format(f))

        # return generator of dive data and its profile data tuples
        nodes = parse(f, q)
        yield ((dive_data(n), dive_profile(n)) for n in nodes)
        i += 1


def _name_parse(name):
    """
    Parse name data from a string. The name string is in simplified BibTeX
    format, i.e.

    - Tom
    - Tom Cora
    - Thomas Henry Corra
    - Corra, Thomas Henry

    Parsed name is tuple consisting of first name, middle name and last
    name.
    """
    f, m, l = None, None, None

    t = name.split(',')
    if len(t) == 1:
        nd = t[0].strip().split(' ', 2)
        if len(nd) == 3:
            f, m, l = nd
        elif len(nd) == 2:
            f, l = nd
        elif len(nd) == 1:
            f = nd[0]
    elif len(t) == 2:
        l = t[0].strip()
        nd = t[1].strip().split(' ', 1)
        f = nd[0]
        if len(nd) == 2:
            m = nd[1]
    else:
        raise ValueError('Cannot parse name')

    if f:
        f = f.strip()
    if m:
        m = m.strip()
    if l:
        l = l.strip()
    return f, m, l


# vim: sw=4:et:ai