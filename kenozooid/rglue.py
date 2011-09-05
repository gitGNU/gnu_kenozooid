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
Rpy integration functions.
"""

import rpy2.robjects as ro
R = ro.r

def float_vec(data):
    """
    Create R float vector using RPy interface.
    """
    # unfortunately, rpy does not convert None to NA anymore
    c = ro.FloatVector([ro.NA_Real if v is None else float(v) for v in data])
    return c


def bool_vec(data):
    """
    Create R bool vector using RPy interface.
    """
    # unfortunately, rpy does not convert None to NA anymore
    c = ro.BoolVector([ro.NA_Bool if v is None else bool(v) for v in data])
    return c

# vim: sw=4:et:ai
