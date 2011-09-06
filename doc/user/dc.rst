.. _user-dc:

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
A dive computer related command can result with an error message like::

    kz: Driver "ostc" cannot communicate with a device at port "/dev/ttyUSB0"

The possible reasons for above message can be

#. Is a dive computer connected to your personal computer? Execute the
   command::

    dmesg -a | less

   and look for output similar to the following::

    usb 2-1.1: new full speed USB device number 4 using ehci_hcd
    usb 2-1.1: New USB device found, idVendor=0403, idProduct=6001
    usb 2-1.1: New USB device strings: Mfr=1, Product=2, SerialNumber=3
    usb 2-1.1: Product: HeinrichsWeikamp OSTC
    usb 2-1.1: Manufacturer: FTDI
    usb 2-1.1: SerialNumber: A4RTV8TO
    USB Serial support registered for FTDI USB Serial Device
    ftdi_sio 2-1.1:1.0: FTDI USB Serial Device converter detected
    usb 2-1.1: Detected FT232RL
    usb 2-1.1: Number of endpoints 2
    usb 2-1.1: Endpoint 1 MaxPacketSize 64
    usb 2-1.1: Endpoint 2 MaxPacketSize 64
    usb 2-1.1: Setting MaxPacketSize 64
    usb 2-1.1: FTDI USB Serial Device converter now attached to ttyUSB1

   At the end of the last line above it is indicated that a dive computer
   is connected to ``/dev/ttyUSB1`` device (not usual ``/dev/ttyUSB0`` used
   across this document).

#. Is the dive computer switched on? Some dive computers will not switch
   automatically on when connected to a personal computer.

#. Are the device file (i.e. ``/dev/ttyUSB0``, ``/dev/ttyUSB1``)
   permissions correct? Execute the command::

    ls -l /dev/ttyUSB0

   The output can be::

    crw-rw---- 1 root dialout 4, 23 Aug 25 01:30 /dev/ttyUSB0

   Above means, that only user ``root`` and users belonging to group
   ``dialout`` have read-write access to dive computer (for more about Unix
   file permissions notation, see the `wikipedia article
   <http://en.wikipedia.org/wiki/Filesystem_permissions#Notation_of_traditional_Unix_permissions>`_).

   Use command ``id`` to check groups your system user belongs to::

    $ id
    uid=1000(ttrav) gid=1000(users) groups=1000(users),10(wheel),16(dialout),17(proc)

.. include:: backup.rst

.. include:: simulation.rst

.. vim: sw=4:et:ai
