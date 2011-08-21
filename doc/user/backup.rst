.. _dc-backup:

Data Backup
-----------
The data in a dive computer memory, like configuration settings or dive
profiles, is usually kept in some binary format specific to a dive computer
model or manufacturer.

Kenozooid ``backup`` command provides functionality to fetch and store such
dive computer memory data in a backup file.

The backup files are useful in several situations

- snapshot of dive computer data is preserved - if data processing software
  uses universal data format independent from dive computer model or
  manufacturer (i.e.  UDDF), then, when new software features or bug fixes
  are implemented, the data in universal format can be extracted from
  a snapshot
- the binary data from a backup can be sent to developers of data parsing
  software to investigate software related problems
- or it can be sent to dive computer manufacturer to investigate dive
  computer related problems

To create a backup file of OSTC dive computer data::

    kz backup ostc /dev/ttyUSB0 backup-ostc-20090214.uddf

or to backup Sensus Ultra data::

    kz backup su /dev/ttyUSB0 backup-su-20090214.uddf

During the backup, Kenozooid extracts dive data from binary data and stores
both binary and dive data in a backup file. This allows to access the dive
computer data with other Kenozooid commands immediately.  For example, to
list the dives (see :ref:`logbook-ls`) from a backup file::

    kz dive list backup-su-20090214.uddf

Dive Data Extraction
^^^^^^^^^^^^^^^^^^^^
Kenozooid provides a command to extract dive data from a backup file
containing dive computer binary data stored. As mentioned above, the
command can be very useful when Kenozooid new functionality or bug fixes
are implemented.

To extract dives from a backup file run ``dive extract`` command::

    kz dive extract backup-su-20090214.uddf backup-su-20090214-01.uddf

The ``dive extract`` command behaves in similar way to backup command - the
dive data is stored along with binary data, which was used as source of
extraction. Therefore, the new file (``backup-su-20090214-01.uddf`` in
above example) can be used as dive extraction source once again and old
file can be removed.

Binary Data Import
^^^^^^^^^^^^^^^^^^
The Kenozooid backup command produces files compliant with UDDF. This
allows to describe stored binary data, i.e. with date and time of fetching
the data and dive computer model information.

There are applications, which dump dive computer memory as binary, raw
file. Such files can be converted (imported) by Kenozooid into UDDF file
with ``convert`` command.

To convert OSTC dive computer binary data into UDDF format::

    kz convert ostc ostc-20090214.dump backup-ostc-20090214.uddf

As in case of ``backup`` and ``dive extract`` commands, the UDDF file
contains both dive data and binary data

- the dive data in UDDF file can be accessed with other Kenozooid commands
- or the UDDF file can be reprocessed with ``dive extract`` command when
  necessary
- the source of conversion can be safely removed

.. vim: sw=4:et:ai
