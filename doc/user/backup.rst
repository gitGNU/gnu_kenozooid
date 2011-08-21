Data Backup
-----------
The simplest approach to store data of a dive computer is to dump its
whole memory (usually binary data of configuration settings and dive
profiles) to a file with very minimal or no processing.

Such backup files can be useful in several situations

- all dive profile data is preserved - if data parsing software uses
  some intermediate, application and user friendly format (UDDF in case of
  Kenozooid), then the binary data can be regenerated, when new software
  features or bug fixes are implemented
- configuration settings of dive computer could be restored after dive
  computer reset
- the binary data from a backup can be sent to developers of data parsing
  software to investigate software related problems
- the binary data from a backup can be sent to dive computer manufacturer
  to investigate dive computer related problems

Run following command to create a backup file of data from OSTC::

    kz backup ostc /dev/ttyUSB0 backup-ostc-20090214.uddf

or from Sensus Ultra::

    kz backup su /dev/ttyUSB0 backup-su-20090214.uddf

The backup files (``backup-su-20090214.uddf`` and ``backup-su-20090214.uddf``
above) contain all binary data from dive computer memory in format
compliant with UDDF standard. When backup is performed, the binary data
is immediately parsed as well, so both binary and application data are
stored in a backup. 

The application data is ready to be used with other Kenozooid commands (see
:ref:`logbook-ls` for the start) and binary data can be regenerated in the
future (see below).

Data Regeneration
^^^^^^^^^^^^^^^^^

Converting Binary Data
^^^^^^^^^^^^^^^^^^^^^^

.. vim: sw=4:et:ai
