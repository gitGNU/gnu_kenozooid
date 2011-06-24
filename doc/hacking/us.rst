.. _us:

User Stories
============

.. _dc:

Dive Computer
-------------

.. _backup:

Backup
^^^^^^
The diver backups dive computer data - configuration and dive profiles.

Dive computer data in its original (highly probably binary) structure is
saved, then processed to Kenozooid data structures and saved. See also
rbackup_.

.. _rbackup:

Backup Reprocess
^^^^^^^^^^^^^^^^
The Kenozooid dive computer drivers can be buggy or not recognize all dive
computer's functionality, therefore there is a need to extract dive
profiles and dive computer configuration once again.

Raw Data Conversion
^^^^^^^^^^^^^^^^^^^
The raw dive computer data can be obtained by other software, therefore
there is a need to convert the raw data into Kenozooid data structures and
save.

The resulting file should be similar or the same as in case of backuping
data directly from a dive computer.

Simulation
^^^^^^^^^^

.. _logbook:

Logbook
-------

.. _adddive:

Add Dive
^^^^^^^^
The diver adds a dive to dive logbook. A dive consists of dive data, which
is

- date
- maximum depth
- dive duration

Optionally, diver can specify

- time of dive
- minimum temperature
- buddy
- dive site

.. _adddivep:

Add Dive With Profile
^^^^^^^^^^^^^^^^^^^^^
The diver adds a dive with profile data to dive logbook.

Some of the dive data is extracted from profile data (i.e. dive duration)
and some is provided by diver (i.e. buddy). See adddive_ for list of dive
data.

Listing Dives
^^^^^^^^^^^^^
The diver lists dives from dive logbook.

By default, all dives are displayed.

The dives output can be limited with

- dive date query
- buddy
- dive site

Dive Date Query
"""""""""""""""
Dive date query should allow to specify

- exact date (day) of a dive, i.e. 2011-12-01, 20111201
- exact date and dive number, i.e. 2011-12-01#3
- range of dates, i.e. 2011-12, 2011-12-01..2011-12-31

The format of date should be based on `ISO 8601 <http://en.wikipedia.org/wiki/ISO_8601>`_,
in particular

- year is 4 digit number
- year is followed by month, month by day

.. _planning:

Planning
--------

Simple Calculation
^^^^^^^^^^^^^^^^^^

.. vim: sw=4:et:ai
