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
Functions for plotting dive profile data.

Plotting functions generate graphs with dive time in minutes of x-axis and
profile data on y-axis (usually depth in meters).

Basic dive information can be shown

- start time of a dive
- time length of a dive
- maximum depth
- minimum temperature during a dive

"""

import rpy2.robjects as ro
R = ro.r

import itertools
import logging

from kenozooid.util import min2str, FMT_DIVETIME
import kenozooid.analyze as ka

log = logging.getLogger('kenozooid.plot')

def plot(fout, dives, title=False, info=False, temp=False, sig=True,
        legend=False, format='pdf'):
    """
    Plot graphs of dive profiles.
    
    :Parameters:
     fout
        Name of output file.
     dives
        Dives and their profiles to be plotted.
     title
        Set plot title.
     info
        Display dive information (time, depth, temperature).
     temp
        Plot temperature graph.
     sig
        Display Kenozooid signature.
     legend
        Display graph legend.
     format
        Format of output file (i.e. pdf, png, svg).
    """
    args = (fout, title, info, temp, sig, format)
    ka.analyze('stats/pplot-details.R', dives, args)


def plot_overlay(fout, dives, title=False, info=False, temp=False, sig=True,
        legend=False, labels=None, format='pdf'):
    """
    Plot dive profiles on one graph.
    
    :Parameters:
     fout
        Name of output file.
     dives
        Dives and their profiles to be plotted.
     title
        Set plot title.
     info
        Display dive information (time, depth, temperature).
     temp
        Plot temperature graph.
     sig
        Display Kenozooid signature.
     legend
        Display graph legend.
     labels
        Alternative labels for dives.
     format
        Format of output file (i.e. pdf, png, svg).
    """
    R("""
library(Hmisc)
library(grid)
library(colorspace)
""")

    _plot_start(fout, format)

    if not title:
        R('par(mar=c(5, 4, 1, 2) + 0.1)')

    R("""
times = list()
depths = list()
    """)

    lstr = []
    for k, (dive, dp) in enumerate(dives):
        log.debug('plotting dive profile') 
        _inject_profile(dp)
        R("""
times[[{k}]] = dp$time / 60.0
depths[[{k}]] = dp$depth
        """.format(k=k + 1))

        lstr.append(dive.datetime.strftime(FMT_DIVETIME))

    k += 1 # total amount of dives

    log.debug('saving graph') 

    # copy labels provided by user
    if not labels:
        labels = []
    for i, l in enumerate(labels):
        if l:
            lstr[i] = l
    ro.globalenv['labels'] = ro.StrVector(lstr)

    R("""
cols = diverge_hcl({nd})

r_time = range(sapply(times, range))
r_depth = range(sapply(depths, range))
plot(NA, xlim=r_time, ylim=rev(r_depth),
    xlab='Time [min]', ylab='Depth [m]')

# first the grid
minor.tick(nx=5, ny=2)
grid()

# then the profiles
for (i in 1:{nd}) {{
    lines(times[[i]], depths[[i]], col=cols[i])
}}
""".format(nd=k))
    if legend:
        R("""
if ({nd} > 10) {{
    lscale = 0.7
}} else {{
    lscale = 1.0
}}
legend('bottomright', labels, col=cols, lwd=1, inset=c(0.02, 0.05),
    ncol=ceiling({nd} / 10), cex=lscale)
        """.format(nd=k))

    if sig:
        _plot_sig()

    R('dev.off()')


# vim: sw=4:et:ai
