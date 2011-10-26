.. _user-plot:

Dive Data Plotting
==================
Plotting of dive profiles can be performed with Kenozooid's ``plot`` command.

Various types of plots are supported

- dive profile details showing dive profile and its details like deco
  ceiling, gas switches, setpoint changes, MOD of used gas, etc.
- dive profile comparison plot

The output of ``plot`` command can be saved in PDF, SVG or PNG formats.
Simply change extension of output file to get desired file format as
a result, i.e.  ``dives.pdf`` - PDF file, ``dives.png`` - PNG file.

Details Plot
------------
Dive profile details plot allows to show dive profiles and associated data - one
dive profile per graph.

By default the graphs are very minimal. For example::

   $ kz plot backup-ostc-20110728.uddf dives.pdf

gives one graph per page in PDF file with no additional information like
dive maximum depth or dive duration.

More information can be added to a plot using appropriate options. For
example to add basic dive information (maximum depth, duration, minimal
temperature) and a title to a plot use ``--info`` and ``--title`` options,
i.e.::

   $ kz plot --info --title backup-ostc-20110728.uddf dives.pdf

The plot can be limited to specific dives, for example to limit plotting to
dives 2,3, 4 and 5::

   $ kz plot --info --title 2-5 backup-ostc-20110728.uddf dives.pdf

Multiple input files can be also specified (plot dives 2, 3, 4 and 5 from
backup-ostc-20110728.uddf and plot dives 6 and 8 from
backup-ostc-20110729.uddf)::

   kz plot 2-5 backup-ostc-20110728.uddf 6,8 backup-ostc-20110729.uddf dives.pdf

.. figure:: /user/dive-2011-06-26.*
   :align: center
   :target: dive-2011-06-26.pdf

   Dive profile plot of 4th dive from ``backup-ostc-20110728.uddf`` file


Comparing Dives
---------------
Kenozooid allows to compare two or more dive profiles on one graph. 
Such functionality can be useful to compare

- data logged by two different dive computers
- several dives made on the same dive site using the same route under the
  water
- profiles of dive buddies

Use ``-t cmp`` option to plot many dives on one plot (as in case of dive
profile details plot, multiple dives from multiple files can be specified),
for example::

    $ kz plot -t cmp --legend --labels Rebreather 'Open Circuit' -- 1,2 logbook.uddf divemode-compare.pdf

Above, Kenozooid is instructed to put a legend on a plot with appropriate
labels (``Rebreather`` and ``Open Circuit``) for dive profiles.

.. figure:: /user/divemode-compare.*
   :align: center
   :target: divemode-compare.pdf

   Rebreather and open circuit dive profiles on a wreck

.. vim: sw=4:et:ai
