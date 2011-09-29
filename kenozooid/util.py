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
Kenozooid utility funtions.
"""

import math
import string

# format for dive time presentation
FMT_DIVETIME = '%Y-%m-%d %H:%M'

def min2str(t):
    """
    Convert decimal minutes (i.e. 38.84) into MM:SS string (i.e. 38:50).

    >>> min2str(38.84)
    '38:50'

    >>> min2str(67.20)
    '67:12'
    """
    return '%02d:%02d' % (int(t), math.modf(t)[0] * 60)


class _Formatter(string.Formatter):
    """
    Formatter, which formats 'None' as empty string.
    """
    def format_field(self, value, fs):
        """
        Format null value as empty string. If value is not null, then
        render it using default method of the formatter.
        """
        if value is None:
            return ''
        else:
            return super(_Formatter, self).format_field(value, fs)


nformat = _Formatter().format


def pipe(data, *gens):
    """
    Pipe data through list of geneators.
    
    :Parameters:
     data
        Data to pipe through the generators.
     gens
        List of generators to process the data.
    """
    for g in gens:
        data = g(data)
    return data


# Return empty iterator if ``it`` is None, otherwise return ``it``
# itself.
nit = lambda it: () if it is None else it

# vim: sw=4:et:ai
