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

import argparse
import logging
import sys

from kenozooid.component import query, params


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



def main():
    """
    Find Kenozooid command line modules and execute them.
    """
    import kenozooid.cli.calc
    import kenozooid.cli.dc
    import kenozooid.cli.uddf

    # add common options to command line parser
    parser = argparse.ArgumentParser(
            description='Kenozooid {0}.'.format(kenozooid.__version__))

    parser.add_argument('-v', '--verbose',
            action='store_true', dest='verbose', default=False,
            help='explain what is being done')
    parser.add_argument('--profile',
            action='store_true', dest='profile', default=False,
            help='run with profiler')

    subp = parser.add_subparsers()

    # find command line modules and create subcommands
    modules = sorted(query(CLIModule), key=lambda cls: params(cls)['name'])
    for cls in modules:
        p = params(cls)

        name = p['name']
        desc = cls.description

        p = subp.add_parser(name, help=desc)
        cls.add_arguments(p)
        p.set_defaults(cmd=name)

    args = parser.parse_args()

    # configure basic logger
    logging.basicConfig()
    logging.Logger.manager.loggerDict.clear()
    log = logging.getLogger()
    log.setLevel(logging.INFO)

    if args.verbose:
        logging.root.setLevel(logging.DEBUG)

    # import modules implementing supported drivers
    # todo: support dynamic import of third party drivers
    from kenozooid.driver import DeviceError
    import kenozooid.driver.dummy
    import kenozooid.driver.ostc
    import kenozooid.driver.su

    # execute the command line module
    try:
        cls = query(name=args.cmd).next()
        cmd = cls()

        if args.profile:
            import hotshot, hotshot.stats
            prof = hotshot.Profile('kenozooid.prof')
            prof.runcall(cmd, args)
            prof.close()
            stats = hotshot.stats.load('kenozooid.prof')
            stats.strip_dirs()
            stats.sort_stats('time', 'calls')
            stats.print_stats(20)
        else:
            cmd(args)
    except DeviceError, ex:
        print >> sys.stderr, 'kz: {0}'.format(ex)
        sys.exit(3)
    except ArgumentError, ex:
        print >> sys.stderr, 'kz: {0}'.format(ex)
        sys.exit(2)
    except StopIteration:
        parser.print_help()
        sys.exit(2)


# vim: sw=4:et:ai
