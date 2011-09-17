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
from kenozooid.units import K2C
import kenozooid.analyze as ka
import kenozooid.rglue as kr

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
    dives, dt = itertools.tee(dives, 2)

    # dive title formatter
    tfmt = lambda d: d.datetime.strftime(FMT_DIVETIME)
    # dive info formatter
    _ifmt = 't = {}\n\u21a7 = {:.1f}m\nT = {:.1f}\u00b0C'.format
    ifmt = lambda d: _ifmt(min2str(d.duration / 60.0), d.depth, K2C(d.temp))
    cols = []
    t_cols = []
    f_cols = []
    if title:
        cols.append('title')
        t_cols.append(ro.StrVector)
        f_cols.append(tfmt)
    if info:
        cols.append('info')
        t_cols.append(ro.StrVector)
        f_cols.append(ifmt)

    # format optional dive data (i.e. title, info); dive per row
    dt = (tuple(map(lambda f: f(d), f_cols)) for d, p in dt)
    ro.globalenv['kz.dives.ui'] = kr.df(cols, t_cols, dt)

    args = (fout, sig, format)
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
    if legend:
        dives, dt = itertools.tee(dives, 2)
        tfmt = lambda d: d.datetime.strftime(FMT_DIVETIME)
        v = [l if l else tfmt(d.datetime) for (d, _), l in zip(dt, labels)]
        df = ro.DataFrame({'label': ro.StrVector(v)})
    else:
        df = ro.DataFrame({})

    ro.globalenv['kz.dives.ui'] = df

    args = (fout, sig, format)
    ka.analyze('stats/pplot-overlay.R', dives, args)



# vim: sw=4:et:ai
