# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2012 by Artur Wroblewski <wrobell@pld-linux.org>
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
Routines for dive profile data plotting.

The R scripts are used for plotting, see stats/pplot-*.R files.

Before R script execution, the kz.dives.ui data frame is injected into R
space to have preformatted dive data like dive title, dive legend label or
dive information ready for a dive graph (and formatted with Python as it is
more convenient).
"""

import itertools
from itertools import zip_longest as lzip
from collections import OrderedDict
import logging

import rpy2.robjects as ro
R = ro.r

from kenozooid.util import min2str, FMT_DIVETIME
from kenozooid.units import K2C
import kenozooid.analyze as ka
import kenozooid.rglue as kr

log = logging.getLogger('kenozooid.plot')

def _inject_dives_ui(dives, title, info, temp, avg_depth,
        legend, labels):

    """
    Inject ``kz.dives.ui`` data frame into R global space.

    The data frame has the following columns

    info
        Dive information string with dive duration, maximum depth and
        dive temperature.
    title
        Dive title.
    avg_depth
        Dive average depth label.
    label
        Dive label put on legend.

    See ``plot`` for parameters description.
    """
    labels = [] if labels is None else labels

    # dive title formatter
    tfmt = lambda d, l: '{}'.format(d.datetime)

    # dive info formatter
    _ifmt = '{:.1f}m \u00b7 {}min \u00b7 {:.1f}\u00b0C'.format
    ifmt = lambda d, l: _ifmt(d.depth, min2str(d.duration / 60.0), K2C(d.temp))

    # average depth formatter
    dfmt = lambda d, l: None if d.avg_depth is None \
                else '{:.1f}m'.format(d.avg_depth)

    # label formatter
    lfmt = lambda d, l: l if l else tfmt(d)

    cols = []
    fmts = []
    if title:
        cols.append('title')
        fmts.append(tfmt)
    if info:
        cols.append('info')
        fmts.append(ifmt)
    if avg_depth:
        cols.append('avg_depth')
        fmts.append(dfmt)
    if legend:
        cols.append('label')
        fmts.append(lfmt)
    vt = (ro.StrVector, ) * len(cols)
    data = (tuple(f(d, l) for f in fmts) for d, l in lzip(dives, labels))
    ui_df = kr.df(cols, vt, data)

    ro.globalenv['kz.dives.ui'] = ui_df


def plot(dives, fout, ptype='details', title=False, info=False, temp=False,
        avg_depth=False, mod=False, sig=True, legend=False, labels=None,
        format='pdf'):
    """
    Plot graphs of dive profiles.
    
    :Parameters:
     dives
        Dives to be plotted.
     fout
        Name of output file.
     ptype
        Plot type converted to R script name ``stats/pplot-*.R``.
     title
        Set plot title.
     info
        Display dive information (time, depth, temperature).
     temp
        Plot temperature graph.
     avg_depth
        Plot dive average depth.
     mod
        Plot MOD of current gas.
     sig
        Display Kenozooid signature.
     legend
        Display graph legend.
     labels
        Alternative legend labels.
     format
        Format of output file (i.e. pdf, png, svg).
    """
    dives, dt = itertools.tee(dives, 2)
    _inject_dives_ui(dt, title=title, info=info, temp=temp,
            avg_depth=avg_depth, legend=legend, labels=labels)

    v = lambda s, t: '--{}'.format(s) if t else '--no-{}'
    args = (fout, format, v('sig', sig), v('mod', mod))
    ka.analyze('pplot-{}.R'.format(ptype), args, dives)


# vim: sw=4:et:ai
