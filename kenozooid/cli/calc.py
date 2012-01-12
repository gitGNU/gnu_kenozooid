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
Kenozooid calculator command line modules.
"""

from kenozooid.cli import CLIModule, ArgumentError
from kenozooid.component import inject


@inject(CLIModule, name='calc')
class Calculate(object):
    """
    Kenozooid calculator command line module.
    """
    description = 'air and nitrox calculations (partial pressure, EAD, MOD); metric units'

    @classmethod
    def add_arguments(cls, parser):
        """
        Parse calculator commands arguments.

        TODO: Add imperial/metric units support.
        """
        cmds = ('ppO2', 'ppN2', 'ead')
        desc = ('calculate O2 partial pressure (ppO2)',
            'calculate Nitrogen parital pressure (ppN2)', 
            'calculate equivalent air depth (EAD)')
        subp = parser.add_subparsers()
        for cmd, d in zip(cmds, desc):
            p = subp.add_parser(cmd, help=d)
            p.set_defaults(cmd_calc=cmd)
            p.add_argument('depth', type=float, nargs=1)
            p.add_argument('ean', type=float, nargs=1)

        p = subp.add_parser('mod',
                help='calculate maximum operating depth (MOD)')
        p.set_defaults(cmd_calc='mod')
        p.add_argument('pp', type=float, nargs='?', default=1.4)
        p.add_argument('ean', type=float, nargs=1)

        p = subp.add_parser('rmv',
                help='calculate respiratory minute volume (RMV)')
        p.set_defaults(cmd_calc='rmv')
        p.add_argument('tank', type=float, nargs=1,
                help='tank size in liters, i.e. 12, 15')
        p.add_argument('pressure', type=float, nargs=1,
                help='pressure difference between start and end of dive,' \
                    ' i.e. 170 (220 - 50)')
        p.add_argument('depth', type=float, nargs=1,
                help='average depth of dive')
        p.add_argument('duration', type=float, nargs=1,
                help='duration of dive in minutes')


    def __call__(self, args):
        """
        Execute Kenozooid calculator command.
        """
        import kenozooid.calc as kcalc

        cmd = args.cmd_calc
        f = getattr(kcalc, cmd)
        if cmd in ('ppO2', 'ppN2', 'ead'):
            result = f(args.depth[0], args.ean[0])
        elif cmd == 'mod':
            result = f(args.ean[0], args.pp)
        elif cmd == 'rmv':
            result = f(args.tank[0], args.pressure[0], args.depth[0],
                    args.duration[0])
        else:
            raise ArgumentError()

        print('{0:.2f}'.format(result))


# vim: sw=4:et:ai
