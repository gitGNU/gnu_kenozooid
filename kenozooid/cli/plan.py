#
# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2013 by Artur Wroblewski <wrobell@pld-linux.org>
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
Kenozooid dive planning commands.
"""

from kenozooid.cli import CLICommand, ArgumentError, \
    add_master_command
from kenozooid.component import inject

# for comand 'plan deco'
add_master_command(
    'plan',
    'Kenozooid dive planning commands',
    'plan a dive'
)


@inject(CLICommand, name='plan deco')
class DecoPlan(object):
    """
    Kenozooid decompression dive planning command.
    """
    description = 'decompression dive planner'

    @classmethod
    def add_arguments(cls, parser):
        """
        Parse decompression dive planner command arguments.
        """
        parser.add_argument('depth', type=int, help='dive depth')
        parser.add_argument('time', type=int, help='dive bottom time')


    def __call__(self, args):
        """
        Execute Kenozooid decompression dive planning command.
        """
        import kenozooid.plan.deco as planner
        from kenozooid.data import gas
        gl = planner.GasList(gas(21, 0))
        plan = planner.plan_deco_dive(gl, args.depth, args.time)
        print(planner.plan_to_text(plan))


# vim: sw=4:et:ai

