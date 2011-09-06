Quick Tour
==========

Call ``kz`` script to execute Kenozooid commands and sub commands, see
:ref:`user-ui` for more. To list the commands::

    $ kz -h
    usage: kz [-h] [-v]
              {analyze,backup,buddy,calc,convert,dive,drivers,plot,sim,site} ...

    Kenozooid 0.1.0.

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose         explain what is being done

    Kenozooid commands:
      {analyze,backup,buddy,calc,convert,dive,drivers,plot,sim,site}
        analyze             analyze dives with R script
        backup              backup dive computer data (logbook, settings, etc.)
        buddy               manage dive buddies in UDDF file
        calc                air and nitrox calculations (partial pressure, EAD,
                            MOD); metric units
        convert             convert binary dive computer data.
        dive                manage dives in UDDF file
        drivers             list available dive computer drivers and their
                            capabilities
        plot                plot graphs of dive profiles
        sim                 simulate dives with a dive computer
        site                manage dive sites in UDDF file

Connect dive computer to a personal computer and backup its data (see also
:ref:`user-dc`)::

   kz backup ostc /dev/ttyUSB0 backup-ostc-20110728.uddf
   kz backup su /dev/ttyUSB0 backup-su-20110728.uddf

Above commands are for OSTC dive computer and Sensus Ultra dive logger.

List the dives from backup file (see also :ref:`user-logbook`)::

    $ kz dive list backup-ostc-20110728.uddf
    backup-ostc-20110728.uddf:
        1: 2011-06-12 21:45     40.8m     58:50     5.4°C
        2: 2011-06-19 12:26     58.8m     48:40     6.2°C
        3: 2011-06-24 13:18     94.1m    107:20     5.1°C
        4: 2011-06-26 12:56     85.0m    104:42     5.5°C
        5: 2011-06-29 21:30     42.7m     57:29     6.2°C
        6: 2011-07-07 21:44     27.5m     60:38     7.0°C
        7: 2011-07-20 21:50     49.9m     65:42     5.7°C
        8: 2011-07-28 21:26     60.2m     64:08     5.7°C


Plot dive profiles::

   kz plot --info --title backup-ostc-20110728.uddf

Plot dive profiles of dives 2, 3, 4 and 5::

   kz plot --info --title 2-5 backup-ostc-20110728.uddf

.. vim: sw=4:et:ai
