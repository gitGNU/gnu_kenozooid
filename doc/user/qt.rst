Quick Tour
==========

Call ``kz`` script to execute Kenozooid commands, see
:ref:`user-ui` for more.

Connect dive computer to a personal computer and backup its data (see also
:ref:`user-dc`)::

   kz backup ostc /dev/ttyUSB0 backup-ostc-20110728.uddf
   kz backup su /dev/ttyUSB0 backup-su-20110728.uddf

Above commands save data from OSTC dive computer and Sensus Ultra dive data
logger to ``backup-ostc-20110728.uddf`` and ``backup-su-20110728.uddf``
files.

File compression is supported. Simply add ``.bz2`` extension to a file
name, for example::

   kz backup ostc /dev/ttyUSB0 backup-ostc-20110728.uddf.bz2
   kz backup su /dev/ttyUSB0 backup-su-20110728.uddf.bz2

List the dives from backup file (see also :ref:`user-logbook`)::

    $ kz dive list backup-ostc-20110728.uddf
    backup-ostc-20110728.uddf:
        1: 2011-06-12 21:45     40.8m ( --- )     58:50     5.4°C
        2: 2011-06-19 12:26     58.8m ( --- )     48:40     6.2°C
        3: 2011-06-24 13:18     94.1m (26.1m)    107:20     5.1°C
        4: 2011-06-26 12:56     85.0m (24.4m)    104:42     5.5°C
        5: 2011-06-29 21:30     42.7m (20.0m)     57:29     6.2°C
        6: 2011-07-07 21:44     27.5m ( 8.4m)     60:38     7.0°C
        7: 2011-07-20 21:50     49.9m (19.6m)     65:42     5.7°C
        8: 2011-07-28 21:26     60.2m (20.9m)     64:08     5.7°C


Plot dive profiles (see :ref:`user-plot`)::

   kz plot --info backup-ostc-20110728.uddf dives.pdf

Plot dive profiles of dives 2, 3, 4 and 5::

   kz plot --info 2-5 backup-ostc-20110728.uddf dives.pdf

.. figure:: /user/dive-2011-06-26.*
   :align: center
   :target: dive-2011-06-26.pdf

   Dive profile plot of 4th dive from ``backup-ostc-20110728.uddf`` backup file

.. vim: sw=4:et:ai
