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
Unit conversion, i.e. Kelvin to Celsius.
"""

def C2K(t):
    """
    Convert temperature from Celsius to Kelvin.
    """
    return t + 273.15


def K2C(t):
    """
    Convert temperature from Kelvin to Celsius.
    """
    return t - 273.15


def B2Pa(p):
    """
    Convert pressure from Bar to Pascal.
    """
    return p * 100000


# vim: sw=4:et:ai
