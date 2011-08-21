.. _dc-backup:

Data Backup
-----------
The data in a dive computer memory, like configuration settings or dive
profiles, is usually kept in some binary format specific to a dive computer
manufacturer or model.

Kenozooid ``backup`` command provides functionality to fetch and store such
dive computer memory data in a backup file.

The backup files are useful in several situations

- snapshot of dive computer data is preserved - if data processing software
  uses universal data format independent from dive computer model or
  manufacturer (i.e.  UDDF), then, when new software features or bug fixes
  are implemented, the data in universal format can be regenerated from
  a snapshot
- the binary data from a backup can be sent to developers of data parsing
  software to investigate software related problems
- or it can be sent to dive computer manufacturer to investigate dive
  computer related problems

To create a backup file of OSTC dive computer data::

    kz backup ostc /dev/ttyUSB0 backup-ostc-20090214.uddf

or to backup Sensus Ultra data::

    kz backup su /dev/ttyUSB0 backup-su-20090214.uddf

During the backup, Kenozooid converts the binary data into universal format
and stores both binary and universal data in a backup file, which allows to
access the dive computer data with other Kenozooid commands immediately.
For example, to list the dives (see :ref:`logbook-ls`) from a backup file::

    kz dive list backup-su-20090214.uddf

The regeneration of data in universal format from binary data stored in a
backup file is described in the next section.

Data Regeneration
^^^^^^^^^^^^^^^^^

Converting Binary Data
^^^^^^^^^^^^^^^^^^^^^^

.. vim: sw=4:et:ai
