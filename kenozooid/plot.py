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
Routines for dive profile data plotting.

The R scripts are used for plotting, see stats/pplot-*.R files.

Before R script execution, the kz.dives.ui data frame is injected into R
space to have preformatted dive data like dive title, dive legend label or
dive information ready for a dive graph (and formatted with Python as it is
more convenient).
"""

import itertools
from collections import OrderedDict
import logging

import rpy2.robjects as ro
R = ro.r

from kenozooid.util import min2str, FMT_DIVETIME
from kenozooid.units import K2C
import kenozooid.analyze as ka
import kenozooid.rglue as kr

log = logging.getLogger('kenozooid.plot')

def _inject_dives_ui(dives, title, info, temp, mod, sig, legend, labels):
    """
    Inject ``kz.dives.ui`` data frame in R space.

    The data frame can be empty but can have any combination of the
    following columns

    info
        Dive information string with dive duration, maximum depth and
        dive temperature.
    title
        Dive title.
    label
        Dive label put on legend.

    See ``plot`` for parameters description.
    """
    dives, dt = itertools.tee(dives, 2)

    # dive title formatter
    tfmt = lambda d: d.datetime.strftime(FMT_DIVETIME)
    # dive info formatter
    _ifmt = '{:.1f}m \u00b7 {}min \u00b7 {:.1f}\u00b0C'.format
    ifmt = lambda d: _ifmt(d.depth, min2str(d.duration / 60.0), K2C(d.temp))
    # create optional columns like title and info
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

    # format optional dive data (i.e. title, info) from dive data;
    # dive per row
    opt_d = (tuple(map(lambda f: f(d), f_cols)) for d, p in dt)
    ui_df = kr.df(cols, t_cols, opt_d)

    # provide optional dive data provided by user
    udf = OrderedDict()
    if legend:
        dives, dt = itertools.tee(dives, 2)
        v = [l if l else tfmt(d.datetime) for (d, _), l in zip(dt, labels)]
        udf['label'] = ro.StrVector(v)

    # merge formatted optional dive data and data provided by user
    if udf:
        if ui_df.ncol > 0:
            ui_df.cbind(ro.DataFrame(udf))
        else:
            ui_df = ro.DataFrame(udf)

    ro.globalenv['kz.dives.ui'] = ui_df


def plot(fout, ptype, dives, title=False, info=False, temp=False,
        mod=False, sig=True, legend=False, labels=None, format='pdf'):
    """
    Plot graphs of dive profiles.
    
    :Parameters:
     fout
        Name of output file.
     ptype
        Plot type converted to R script name ``stats/pplot-*.R``.
     dives
        Dives and their profiles to be plotted.
     title
        Set plot title.
     info
        Display dive information (time, depth, temperature).
     temp
        Plot temperature graph.
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

    _inject_dives_ui(dt, title=title, info=info, temp=temp, mod=mod,
            sig=sig, legend=legend, labels=labels)

    v = lambda s, t: '--{}'.format(s) if t else '--no-{}'
    args = (fout, format, v('sig', sig), v('mod', mod))
    ka.analyze('pplot-{}.R'.format(ptype), dives, args)


# vim: sw=4:et:ai
