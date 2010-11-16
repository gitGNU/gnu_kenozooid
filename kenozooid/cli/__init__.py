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

from kenozooid.component import query, params


class CLIModule(object):
    """
    Command line module for Kenozooid.
    """
    usage = ''
    description = ''

    # option group description
    group = None

    def add_options(self, parser):
        """
        Add options of command line module to command line parser.

        :Parameters:
         parser
            Option parser instance.
        """

    def __call__(self, options, *args):
        """
        Execute command line module.

        May raise ArgumentError exception to indicate wrong arguments.

        :Parameters:
         options
            Command line module options.
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

    names = []
    usage = []
    desc = []

    # find command line modules and create command line help text
    modules = sorted(query(CLIModule), key=lambda cls: params(cls)['name'])
    part1 = '\n'
    part2 = ''
    for cls in modules:
        p = params(cls)
        name = p['name']
        usage = cls.usage
        desc = cls.description
        part1 += '\n    %%prog [options] %s %s' % (name, usage)
        part2 += '\n    %s - %s' % (name, desc)

    usage = '%s\n\nCommmand Description:\n%s' % (part1, part2)

    # add common options to command line parser
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-v', '--verbose',
            action='store_true', dest='verbose', default=False,
            help='explain what is being done')
    parser.add_option('--profile',
            action='store_true', dest='profile', default=False,
            help='run with profiler')

    # add command line modules' options to parser
    modules = query(CLIModule)
    for cls in modules:
        m = cls()
        m.add_options(parser)

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

    # find the command line module to be executed
    found = False
    try:
        modules = query(name=args[0])
        cls = modules.next()
        cmd = cls()
        found = True
    except (StopIteration, IndexError):
        parser.print_help()
        sys.exit(1)

    # execute the command line module
    try:
        if options.profile:
            import hotshot, hotshot.stats
            prof = hotshot.Profile('kenozooid.prof')
            prof.runcall(cmd, parser, options, *args)
            prof.close()
            stats = hotshot.stats.load('kenozooid.prof')
            stats.strip_dirs()
            stats.sort_stats('time', 'calls')
            stats.print_stats(20)
        else:
            cmd(options, *args)
    except DeviceError, ex:
        print ex
    except ArgumentError:
        parser.print_help()
        sys.exit(2)


# vim: sw=4:et:ai
