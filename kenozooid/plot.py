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
Plot dive profile graph.

Basic dive information is shown

- time of the dive
- maximum depth
- temperature

Showing any statistical information (like average temperature or depth) is
out of scope, now.
"""

from lxml import etree
import math
import logging

import matplotlib
matplotlib.use('cairo')

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from kenozooid.uddf import get_time
from kenozooid.units import K2C
from kenozooid.util import min2str

log = logging.getLogger('kenozooid.plot')


def plot_dive(tree, dive, fout, title=True, info=True, temp=True):
    """
    Plot dive profile graph using Matplotlib library.

    Dive data are fetched from parsed UDDF file (using ETree) and graph is
    saved into graphical file. Type of graphical file depends on output
    file extension and is handled by Matplotlib library.

    :Parameters:
     tree
        XML file parsed with ETree API.
     dive
        Dive node.
     fout
        Output filename.
     title
        Set plot title.
     info
        Display dive information (time, depth, temperature).
     temp
        Plot temperature graph.
    """
    samples = dive.findall('samples/waypoint')
    depths = [float(s[0].text) for s in samples]
    times = [float(s[1].text) / 60 for s in samples]
    temps = [K2C(float(s[2].text)) for s in samples if len(s) == 3]
    temp_times = [float(s[1].text) / 60 for s in samples if len(s) == 3]

    dive_time = get_time(dive)

    left, width = 0.10, 0.85
    rect1 = [left, 0.25, width, 0.7]
    rect2 = [left, 0.05, width, 0.10]
    axesBG  = '#f6f6f6'
    if temp:
        ax_depth = plt.axes(rect1, axisbg=axesBG)
        ax_temp = plt.axes(rect2, axisbg=axesBG, sharex=ax_depth)
    else:
        ax_depth = plt.axes(axisbg=axesBG)

    #ax_depth.plot(times, depths, label='air')
    ax_depth.plot(times, depths)

    # reverse y-axis, to put 0m depth at top and max depth at the bottom of
    # graph
    ymin, ymax = ax_depth.get_ylim()
    ax_depth.set_ylim([ymax, ymin])

    if title:
        ax_depth.set_title('%s' % dive_time)
    ax_depth.set_xlabel('Time [min]')
    ax_depth.set_ylabel('Depth [m]')
    ax_depth.legend(loc='lower right', shadow=True)
    if info:
        ax_depth.text(0.8, 0.1,
            u't = %s\n\u21a7 = %.2fm\nT = %.1f\u00b0C' \
                % (min2str(times[-1]), max(depths), min(temps)),
            family='monospace',
            transform=ax_depth.transAxes,
            bbox=dict(facecolor='white', edgecolor='none'))
    ax_depth.grid(True)

    if temp:
        ax_temp.set_ylim(math.floor(min(temps)), math.ceil(max(temps)))
        ax_temp.set_ylabel(u'T [\u00b0C]')
        ax_temp.plot(temp_times, temps)
        for l in ax_temp.get_yticklabels():
            l.set_fontsize(9) 
        ax_temp.grid(True)
        ax_temp.yaxis.set_major_locator(MaxNLocator(4))

    # save dive plot and clear matplotlib space
    plt.savefig(fout, papertype='a4')
    plt.clf()


def plot(fin, fout, dives=None, title=True, info=True, temp=True):
    """
    Plot graphs of dive profiles using Matplotlib library.
    
    :Parameters:
     fin
        UDDF file containing dive profile.
     fout
        Output, graphical file.
     title
        Set plot title.
     info
        Display dive information (time, depth, temperature).
     temp
        Plot temperature graph.
     dives
        Dives to be plotted.
    """
    f = open(fin)
    tree = etree.parse(f)
    f.close()

    nodes = tree.findall('//dive')
    n = len(nodes)
    if dives is None:
        dives = range(1, n + 1)
    for i in dives:
        if i > n: # i.e. range was 4-5 and there are only 4 dives
            log.warn('dive number %02d does not exist' % i)
            break
        plot_dive(tree, nodes[i - 1], fout.replace('.', '-%03d.' % i), title, info, temp)

