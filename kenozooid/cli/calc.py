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
Kenozooid calculator command line modules.
"""

from kenozooid.cli import CLIModule, ArgumentError
from kenozooid.component import inject


@inject(CLIModule, name='calc')
class Calculate(object):
    """
    Kenozooid calculator command line module.
    """
    usage = '<ppO2|ppN2|ead <depth> <ean>> | <mod [pp=1.4] <ean>>'
    description = 'air and nitrox calculations (partial pressure, EAD, MOD); metric units'
    def add_options(self, parser):
        """
        No options for calculator. TODO: Add imperial/metric units.
        """

    def __call__(self, options, *args):
        """
        Execute Kenozooid calculator command.
        """
        import kenozooid.calc as kcalc

        fname = args[1]
        if fname in ('ppO2', 'ppN2', 'ead'):
            if len(args) != 4: # fname, depth, ean
                raise ArgumentError()

            depth = float(args[2])
            ean = float(args[3])
            f = getattr(kcalc, fname)
            result = f(depth, ean)

        elif fname == 'mod':
            # fname, [pp], depth
            if len(args) == 3:
                ean = float(args[2])
                pp = 1.4
            elif len(args) == 4:
                pp = float(args[2])
                ean = float(args[3])
            else:
                raise ArgumentError()

            result = kcalc.mod(ean, pp=pp)

        else:
            raise ArgumentError()

        print '%s: %.2f' % (fname, round(result, 2))


# vim: sw=4:et:ai
