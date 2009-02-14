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

import os.path

"""
Kenozooid utility funtions.
"""

def save(filename, data):
    """
    Save data to a file.

    `True` is returned when file is saved. If file already exists, then it
    is not saved and `False` is returned.

    :Parameters:
     filename
        Name of file to be saved.
     data
        Iterator of data to be saved.
    """
    if os.path.exists(filename):
        return False

    with open(filename, 'w') as f:
        for bits in data:
            f.write(bits)

    return True

