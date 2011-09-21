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
Dive analytics via R statistical package.
"""

import rpy2.robjects as ro
import logging
import pkg_resources
import os.path

import kenozooid.uddf as ku
import kenozooid.rglue as kr

log = logging.getLogger('kenozooid.analyze')
R = ro.r

# maximum size of R script, 1MB should be more than enough;
# we need to pass whole script to R to support multi-line
# statements
MAX_SCRIPT_SIZE = 1024 ** 2

def analyze(script, dives, args):
    """
    Analyze dives with specified R script.

    The dive data is converted into R data frames and script is executed in
    the context of the converted data.

    :Parameters:
     script
        R script to run in the context of dive data.
     dives
        Dive data.
     args
        R script arguments.
    """
    if os.path.exists(script):
        log.debug('opening {} script as file'.format(script))
        f = open(script, 'rb')
    else:
        log.debug('opening {} script as resource'.format(script))
        f = pkg_resources.resource_stream('kenozooid',
                'stats/{}'.format(script))

    kr.inject_dive_data(dives)

    if args:
        ro.globalenv['kz.args'] = ro.StrVector(args)
    else:
        R('kz.args = list()')

    data = f.read(MAX_SCRIPT_SIZE)
    if f.read(1):
        raise ValueError('The script {} is too long'.format(script))
    R(data.decode())
    f.close()


# vim: sw=4:et:ai
