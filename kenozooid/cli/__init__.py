#
# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2014 by Artur Wroblewski <wrobell@pld-linux.org>
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
import argparse

from kenozooid.component import query, params, inject

class CLICommand(object):
    """
    Kenozooid's command.
    """
    description = ''

    @classmethod
    def add_arguments(self, parser):
        """
        Add a command arguments to command line parser.

        :Parameters:
         parser
            Parser instance.
        """

    def __call__(self, args):
        """
        Execute Kenozooid command.

        May raise ArgumentError exception to indicate wrong arguments.

        :Parameters:
         args
            Command arguments.
        """



class ArgumentError(BaseException):
    """
    Error to indicate incorrect Kenozooid command arguments.
    """



class NoCommandError(BaseException):
    """
    No Kenozooid command specified.

    :Attributes:
     parser
        Parser command for which error is raised.
    """
    def __init__(self, parser):
        self.parser = parser



class UDDFInputAction(argparse.Action):
    """
    Parse arguments being a list of UDDF input files with '-k' option per
    input file.
    """
    def __call__(self, parser, namespace, values, opt=None):
        arg = getattr(namespace, self.dest)
        if arg is None:
            arg = [], []
            setattr(namespace, self.dest, arg)

        def check(q, f):
            if not hasattr(parser, '__no_f_check__') and not os.path.exists(f):
                parser.error('File {} does not exists'.format(f))

        if opt:
            arg[0].append(None)
            arg[1].append(None)
        else:
            i = 0
            while i < len(values):
                if arg[0] and (arg[0][-1], arg[1][-1]) == (None, None):
                    if i + 1 >= len(values):
                        parser.error('option -k: expected 2 arguments')

                    q, f = values[i], values[i + 1]
                    i += 2
                    check(q, f)
                    arg[0][-1] = q
                    arg[1][-1] = f
                elif values[i] == '-k':
                    arg[0].append(None)
                    arg[1].append(None)
                    i += 1
                else:
                    q, f = None, values[i]
                    i += 1
                    check(q, f)
                    arg[0].append(q)
                    arg[1].append(f)
        assert len(arg[0]) == len(arg[1])


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
    m_subp = parser.add_subparsers(dest='subcmd', title=title)
    c_subp = None # current subparser

    # find Kenozooid commands and sort them by their names
    commands = sorted(query(CLICommand), key=lambda cls: params(cls)['name'])

    for cls in commands:
        p = params(cls)
        name = p['name']
        master = p.get('master', False)
        desc = cls.description
        title = cls.title if master else None

        if ' '  in name:
            assert c_subp # no master command, no subcommand
            cmd, subcmd = name.split()
            p = c_subp.add_parser(subcmd, help=desc)
        else:
            cmd, subcmd = name, name
            p = m_subp.add_parser(subcmd, help=desc)
            if master: # add master command
                c_subp = p.add_subparsers(dest='subcmd', title=title)
            else:
                c_subp = None

        p.set_defaults(cmd=name, parser=p)
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

    @inject(CLICommand, name=name, master=True)
    class Command(object):

        title = None
        description = desc

        @classmethod
        def add_arguments(self, parser):
            pass

        def __call__(self, args):
            raise NoCommandError(args.parser)

    Command.title = title

    return Command


def add_uddf_input(parser):
    """
    Add list of UDDF files as input argument to a parser.

    The function adds several options and arguments

    - `-n` is added to fetch dives by their number
    - multiple UDDF files can be specified
    - each file can be preceded with `-k` option to indicate which dives
      should be fetched from a file

    The `-k` and `-n` options are glued with 'and' operator - use only one
    of them if confused.

    :Parameters:
     parser
        ``argparse`` library parser.
    """
    parser.add_argument('-n',
            dest='dives',
            help='fetch dives with their number (i.e. 40-42,45 are dives'
                ' with dive number 40, 41, 42 and 45)')
    parser.add_argument('-k',
            dest='input',
            nargs=0,
            action=UDDFInputAction,
            help=argparse.SUPPRESS)
    parser.add_argument('input',
            nargs='+',
            action=UDDFInputAction,
            metavar='[-k dives] input',
            help='dives from specified UDDF file (i.e. 1-3,6 is dive'
                ' 1, 2, 3, and 6 from a file, all by default)')
    parser.add_argument('input',
            nargs=argparse.REMAINDER,
            action=UDDFInputAction,
            help=argparse.SUPPRESS)


# vim: sw=4:et:ai
