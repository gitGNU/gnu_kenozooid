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
Commmand line user interface.
"""

import os
import os.path
import itertools
import argparse

import kenozooid.uddf as ku
from kenozooid.component import query, params, inject

class CLIModule(object):
    """
    Command line module for Kenozooid.
    """
    description = ''

    @classmethod
    def add_arguments(self, parser):
        """
        Add command line module arguments to command line parser.

        :Parameters:
         parser
            Parser instance.
        """

    def __call__(self, args):
        """
        Execute command line module.

        May raise ArgumentError exception to indicate wrong arguments.

        :Parameters:
         args
            Command line module arguments.
        """



class ArgumentError(BaseException):
    """
    Wrong command line module arguments.
    """


class UDDFInputAction(argparse.Action):
    """
    Parse arguments being a list of UDDF input files with '-k' option per
    input file.
    """
    def __call__(self, parser, namespace, values, opt=None):
        v = getattr(namespace, self.dest)
        if v is None:
            v = []
            setattr(namespace, self.dest, v)

        def check(q, f):
            if not hasattr(parser, '__no_f_check__') and not os.path.exists(f):
                parser.error('File {} does not exists'.format(f))

        if opt:
            v.append((None, None))
        else:
            i = 0
            while i < len(values):
                if v and v[-1] == (None, None):
                    if i + 1 >= len(values):
                        parser.error('argument -k: expected 2 arguments')

                    q, f = values[i], values[i + 1]
                    i += 2
                    check(q, f)
                    v[-1] = q, f
                elif values[i] == '-k':
                    v.append((None, None))
                    i += 1
                else:
                    q, f = '1-', values[i]
                    i += 1
                    check(q, f)
                    v.append((q, f))


def add_commands(parser, prefix=None, title=None):
    """
    Find and add commands to the argument parser.

    :Parameters:
     parser
        Argument parser (from argparse module).
     prefix
        Prefix of commands to add to argument parser.
     title
        Help title of commands.
    """
    subp = parser.add_subparsers(title=title)

    # find command line modules sorted by their names
    modules = sorted(query(CLIModule), key=lambda cls: params(cls)['name'])
    for cls in modules:
        desc = cls.description

        p = params(cls)
        name = p['name']
        master = p.get('master', False)

        # no prefix then simply use name as command, command shall have no
        # spaces;
        # if there is prefix then match command with its prefix
        if prefix:
            if not name.startswith(prefix) or name == prefix:
                continue

            cmd = name.rsplit(' ', 1)[1]
        elif ' ' in name:
            continue
        else:
            cmd = name

        p = subp.add_parser(cmd, help=desc)
        if not master:
            p.set_defaults(cmd=name)
        cls.add_arguments(p)


def add_master_command(name, title, desc):
    """
    Add master command.

    The purpose of master command is to
    
    - group other commands as sub-commands, i.e. 'dive' master command for
      'list' and 'add' sub-commands means there are 'dive list' and 'dive
      add' commands.
    - provide help title and generalized help description of groupped
      sub-commands

    :Parameters:
     name
        Command name.
     title
        Command help title.
     desc
        Command description.
    """

    @inject(CLIModule, name=name, master=True)
    class Command(object):

        description = desc

        @classmethod
        def add_arguments(self, parser):
            add_commands(parser, name, title)

        def __call__(self, args):
            raise ArgumentError()
    return Command


def add_uddf_input(parser):
    """
    Add list of UDDF files as input argument to a parser.

    :Parameters:
     parser
        ``argparse`` library parser.
    """
    parser.add_argument('-k',
            dest='input',
            nargs=0,
            action=UDDFInputAction,
            help=argparse.SUPPRESS)
    parser.add_argument('input',
            nargs='+',
            action=UDDFInputAction,
            metavar='[-k dives] input',
            help='dives from specified UDDF file (i.e.  1-3,6 is dive'
                ' 1, 2, 3, and 6 from a file, all by default)')
    parser.add_argument('input',
            nargs=argparse.REMAINDER,
            action=UDDFInputAction,
            help=argparse.SUPPRESS)


def find_dive_nodes(*args):
    """
    Find dive nodes in UDDF files using optional node ranges as search
    parameter.

    Each argument is a two item tuple

    - node range, ``None`` if all nodes to be found
    - UDDF file name

    The flattened iterator of nodes is returned.

    :Parameters:
     args
        List of pairs of node ranges and file names.

    .. seealso:: :py:func:`node_range`
    .. seealso:: :py:func:`find_dives`
    """
    Q = '//uddf:dive'
    query = lambda r: Q + '[{}]'.format(ku.node_range(r)) if r else Q
    nodes = (ku.find(f, query(q)) for q, f in args)
    return itertools.chain(*nodes)


def find_dives(*args):
    """
    Find dive data in UDDF files using optional node ranges as search
    parameter.

    Each argument is a two item tuple

    - node range, ``None`` if all nodes to be found
    - UDDF file name

    The flattened iterator of nodes is returned.

    :Parameters:
     args
        List of pairs of node ranges and file names.

    .. seealso:: :py:func:`node_range`
    .. seealso:: :py:func:`find_dive_nodes`
    """
    return ((ku.dive_data(n), ku.dive_profile(n)) \
            for n in find_dive_nodes(*args))
        


# vim: sw=4:et:ai
