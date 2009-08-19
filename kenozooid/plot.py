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
"""

from lxml import etree
import math

import matplotlib
matplotlib.use('cairo')

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

def plot(finput, foutput):
    """
    Plot dive profile graph using Matplotlib library.
    
    Data is fetched from UDDF file and saved into graphical file. Type of
    graphical file depends on output file extension and is handled by
    Matplotlib library.

    :Parameters:
     finput
        UDDF file containing dive profile.
     foutput
        Output, graphical file.
    """
    f = open(finput)
    tree = etree.parse(f)
    f.close()

    samples = tree.xpath('//dive[1]//waypoint') 
    depths = [float(s[0].text) for s in samples]
    times = [float(s[1].text) / 60 for s in samples]

    left, width = 0.10, 0.85
    rect1 = [left, 0.25, width, 0.7]
    rect2 = [left, 0.05, width, 0.10]
    axesBG  = '#f6f6f6'
    ax_depth = plt.axes(rect1, axisbg=axesBG)
    ax_temp = plt.axes(rect2, axisbg=axesBG, sharex=ax_depth)

    #ax_depth.plot(times, depths, label='air')
    ax_depth.plot(times, depths)

    # reverse y-axis, to put 0m depth at top and max depth at the bottom of
    # graph
    ymin, ymax = ax_depth.get_ylim()
    ax_depth.set_ylim([ymax, ymin])

    ax_depth.set_xlabel('Time [min]')
    ax_depth.set_ylabel('Depth [m]')
    ax_depth.legend(loc='lower right', shadow=True)
    ax_depth.grid(True)

    times = [float(s[1].text) / 60 for s in samples if len(s) == 3]
    temps = [float(s[2].text) - 273.15 for s in samples if len(s) == 3]
    ax_temp.set_ylim(math.floor(min(temps)), math.ceil(max(temps)))
    ax_temp.plot(times, temps)
    ax_temp.text(0.58, 0.1,
        # \u2103
        u'min: %.2f\u00b0C  max: %.2f\u00b0C  avg: %.2f\u00b0C' % (min(temps), max(temps), sum(temps)/len(temps)),
        transform=ax_temp.transAxes, fontsize=9,
        bbox=dict(facecolor='white', edgecolor='none'))
    ax_temp.set_ylabel(u'T [\u00b0C]')
    #ax_temp.set_yticks([round(min(temps), 2), round(sum(temps)/len(temps), 2), round(max(temps), 2)])
    for l in ax_temp.get_yticklabels():
        l.set_fontsize(9) 
    ax_temp.grid(True)
    ax_temp.yaxis.set_major_locator(MaxNLocator(4))

    plt.savefig(foutput)


