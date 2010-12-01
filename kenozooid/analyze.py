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
Dive analytics via R statistical package.
"""

import itertools
import rpy2.robjects as ro
import logging

import kenozooid.uddf as ku

log = logging.getLogger('kenozooid.plot')
R = ro.r

def analyze(script, dives):
    """
    Analyze dives with specified R script.

    The dive data is converted into R data frames and script is executed in
    the context of the converted data.

    :Parameters:
     script
        R script to run in the context of dive data.
     dives
        Dive data.
    """
    with open(script) as f:
        dive_times = []

        profiles = ro.DataFrame({})

        for dive, dp in dives:
            dt = ku._format_time(dive.time)
            dive_times.append(dt)

            vtime, vdepth, vtemp = zip(*dp)
            profiles = profiles.rbind(ro.DataFrame({
                'dive': ro.StrVector([dt]),
                'time': ro.FloatVector(vtime),
                'depth': ro.FloatVector(vdepth),
                'temp': ro.FloatVector(vtemp),
            }))
            

        ro.globalenv['dives'] = ro.DataFrame({'time': ro.StrVector(dive_times)})
        ro.globalenv['profiles'] = profiles
        R("""
dives$time = as.POSIXct(dives$time)
profiles$dive = as.POSIXct(profiles$dive)
        """)

        for l in f:
            R(l)

# vim: sw=4:et:ai
