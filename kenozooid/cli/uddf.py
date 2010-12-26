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
import os
import os.path
from functools import partial
from io import BytesIO
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
        parser.add_argument('--csv',
                action='store_true',
                dest='dives_csv',
                default=False,
                help='list dives in CSV format')
        parser.add_argument('input',
                nargs='+',
                help='UDDF file with dive profiles')


    def __call__(self, args):
        """
        Execute command for list of dives in UDDF file.
        """
        from kenozooid.uddf import parse, dive_data, dive_profile
        from kenozooid.util import min2str, FMT_DIVETIME

        csv = args.dives_csv
        files = args.input

        if csv:
            print('file,number,start_time,time,depth')
        for fin in files:
            nodes = parse(fin, '//uddf:dive')
            dives = ((dive_data(n), dive_profile(n)) for n in nodes)

            if not csv:
                print(fin + ':')
            for i, (d, dp) in enumerate(dives):
                vtime, vdepth, vtemp = zip(*dp)
                depth = max(vdepth)
                if csv:
                    fmt = '{file},{no},{stime},{dtime},{depth:.1f}'
                    dtime = max(vtime)
                else:
                    fmt = '{no:4}: {stime}   t={dtime}   \u21a7{depth:.1f}m' 
                    dtime = min2str(max(vtime) / 60.0)
                print(fmt.format(no=i + 1,
                        stime=format(d.time, FMT_DIVETIME),
                        dtime=dtime,
                        depth=depth,
                        file=fin))


@inject(CLIModule, name='dive add')
class AddDives(object):
    """
    Add dives to UDDF file.
    """
    description = 'add dives to UDDF file'

    @classmethod
    def add_arguments(self, parser):
        """
        Add options for dive adding to UDDF file.
        """
        g = parser.add_mutually_exclusive_group(required=True)
        g.add_argument('-d', nargs=3, metavar=('time', 'depth', 'duration'),
                help='add dive with dive time, maximum depth and dive'
                ' duration data')
        g.add_argument('-p', nargs=2, metavar=('dive', 'profile'),
                help='add dive data from an UDDF file containing dive profiles')

        parser.add_argument('-s', '--site', metavar='site',
                help='dive site id or name')
        parser.add_argument('-b', '--buddy', metavar='buddy',
                help='dive buddy id, name or organization member id number')
        parser.add_argument('output', nargs=1, help='UDDF output file')


    def __call__(self, args):
        """
        Execute command for adding dives into UDDF file.
        """
        raise ArgumentError('Not implemented yet')


@inject(CLIModule, name='site add')
class AddDiveSites(object):
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
        raise ArgumentError('Not implemented yet')


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
class ListBuddies(object):
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
                nargs='?',
                help='buddy search string; matches id, member number or'
                ' partially firstname or lastname')
        parser.add_argument('input',
                nargs=1,
                help='UDDF file with dive buddies')


    def __call__(self, args):
        """
        Execute command for removal of dive buddies in UDDF file.
        """
        import kenozooid.uddf as ku

        query = partial(ku.XP_FIND_BUDDY, buddy=args.buddy)
        fin = args.input[0]
        fbk = '{}.bak'.format(fin)

        doc = et.parse(fin)
        ku.remove_nodes(doc, query, buddy=args.buddy)
        os.rename(fin, fbk)
        try:
            ku.save(doc.getroot(), fin)
        except Exception as ex:
            os.rename(fbk, fin)
            raise ex


@inject(CLIModule, name='convert')
class ConvertFile(object):
    """
    Convert UDDF dive memory dumps into UDDF dive profiles.
    """
    description = 'convert UDDF dive memory dumps into UDDF dive profiles'

    @classmethod
    def add_arguments(self, parser):
        """
        Add convert command line command arguments.
        """
        parser.add_argument('input',
                nargs='+',
                help='UDDF file containing dive memory dump')
        parser.add_argument('output',
                nargs=1,
                help='UDDF file to contain dive profiles')


    def __call__(self, args):
        """
        Execute file conversion command.
        """
        from kenozooid.driver import MemoryDump, find_driver
        import kenozooid.uddf as ku

        fin = args.input
        fout = args.output[0]

        pd = ku.create()

        xp_dc = ku.XPath('//uddf:divecomputerdump')
        xp_owner = ku.XPath('//uddf:diver/uddf:owner')

        for fn in fin:
            dd = et.parse(fn)
            nodes = xp_dc(dd)

            if not nodes:
                log.warn('no dive computer dump data found in ' + fn)
                continue

            assert len(nodes) == 1

            dump = ku.dump_data(nodes[0])

            log.debug('dive computer dump data found: ' \
                    '{0.dc_id}, {0.dc_model}, {0.time}'.format(dump))

            dc = ku.create_dc_data(xp_owner(pd)[0], dc_model=dump.dc_model)
            dc_id = dc.get('id')
            dump = dump._replace(dc_id=dc_id, data=BytesIO(dump.data))

            # determine device driver to parse the dump and convert dump
            # data into UDDF profile data
            dumper = find_driver(MemoryDump, dump.dc_model, None)
            dnodes = dumper.convert(dump)
            _, rg = ku.create_node('uddf:profiledata/uddf:repetitiongroup', parent=pd)
            for n in dnodes:
                equ, l = ku.create_node('uddf:equipmentused/uddf:link')
                l.set('ref', dc_id)
                n.insert(1, equ) # append after datetime element
                rg.append(n)

        ku.reorder(pd)
        ku.save(pd, fout)



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
        import itertools
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
        parser.add_argument('input', nargs='+', metavar='[dives] input',
                help='dives from specified UDDF file (i.e.  1-3,6 is dive'
                    ' 1, 2, 3, and 6 from a file, all by default)')


    def __call__(self, args):
        """
        Execute dives' analyze command.
        """
        from kenozooid.analyze import analyze

        # fetch dives and profiles from files provided on command line
        data = itertools.chain(*_fetch(args.input))
        analyze(args.script[0], data)


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
