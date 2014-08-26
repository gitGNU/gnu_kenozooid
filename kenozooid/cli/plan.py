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
Kenozooid dive planning commands.
"""

from kenozooid.cli import CLICommand, ArgumentError, add_master_command
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
        parser.add_argument(
            'gas_list',
            help='gas list, i.e. "air" or "air ean50@20 o2"'
        )
        parser.add_argument('depth', type=int, help='dive depth')
        parser.add_argument('time', type=int, help='dive bottom time')
        parser.add_argument(
            '--rmv', '-r', dest='rmv', default=20, type=int,
            help='respiratory minute volume, i.e. 16 [l/min]'
        )
        parser.add_argument(
            '-6', dest='last_stop_6m', action='store_true', default=False,
            help='last stop at 6m'
        )
        parser.add_argument(
            '--gf-low', '-gl', dest='gf_low', default=30, type=int,
            help='GF Low, i.e. 30 [%%]'
        )
        parser.add_argument(
            '--gf-high', '-gh', dest='gf_high', default=85, type=int,
            help='GF High, i.e. 85 [%%]'
        )


    def __call__(self, args):
        """
        Execute Kenozooid decompression dive planning command.
        """
        import kenozooid.plan.deco as planner
        plan = planner.DivePlan()

        plan.rmv = args.rmv
        plan.last_stop_6m = args.last_stop_6m
        plan.gf_low = args.gf_low
        plan.gf_high = args.gf_high

        gas_list = planner.parse_gas_list(*args.gas_list.split())

        try:
            planner.plan_deco_dive(plan, gas_list, args.depth, args.time)
        except planner.DivePlanError as ex:
            raise ArgumentError(ex)

        print(planner.plan_to_text(plan))


# vim: sw=4:et:ai
