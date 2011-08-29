Dive Computer Support
=====================
Overview
--------
Kenozooid allows to fetch data from dive computers produced by different
manufacturers. Also, it is possible to use some unique features of specific
dive computers like performing simulation (or in the future changing dive
computer configuration).

For each dive computer supported by Kenozooid, there is a driver
implemented with appropriate capabilities.

The supported dive computers and their drivers are listed in the table
below.

+--------------------------+--------+
| Dive computer            | Driver |
+==========================+========+
| OSTC, OSTC Mk.1, OSTC N2 | ostc   |
+--------------------------+--------+
| Sensus Ultra             | su     |
+--------------------------+--------+

To list the capabilities of dive computers (see below for description)
execute ``drivers`` command::

    kz drivers

which gives the following output::

    Available drivers:

    dummy (Dummy Device Driver): simulation
    ostc (OSTC Driver): simulation, backup
    su (Sensus Ultra Driver): backup

The device driver ids (``dummy``, ``ostc``, ``su`` above) should be used
with Kenozooid dive computer related commands like ``backup``, ``convert``
or simulation commands, for example::

    kz backup ostc /dev/ttyUSB0 backup-ostc-20090214.uddf
    kz convert ostc ostc-20090214.dump backup-ostc-20090214.uddf
    kz sim replay ostc /dev/ttyUSB0 1 backup-ostc-20090214.uddf

Driver Capabilities
^^^^^^^^^^^^^^^^^^^
The list of possible dive computer driver capabilities is as follows

    backup
        Dive computer data backup to fetch configuration and all stored
        dive data with dive profiles, see :ref:`dc-backup`.
    simulation
        Switch dive computer into dive mode and perform real time dive
        simulation, see :ref:`dc-simulation`.
        

Troubleshooting
^^^^^^^^^^^^^^^

.. include:: backup.rst

.. include:: simulation.rst

.. vim: sw=4:et:ai
