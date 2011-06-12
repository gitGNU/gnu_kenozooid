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
Commmand line user interface.
"""

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


# vim: sw=4:et:ai
