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

.. _us-sim-plan:

Dive Plan Simulation
^^^^^^^^^^^^^^^^^^^^
Some of the dive computers allow to enter dive mode and simulate a dive
with dive computer buttons, by controlling it from a personal computer or
by using both techniques.

The diver starts simulation on a dive computer from a personal computer
to simulate a dive plan.

.. _us-sim-replay:

Dive Replay
^^^^^^^^^^^
The diver starts dive simulation on a dive computer from a personal
computer to replay a dive profile stored in dive logbook.

.. _us-logbook:

Logbook
-------

.. _adddive:

Add Dive
^^^^^^^^
The diver adds a dive to dive logbook. A dive consists of dive data.
The data is

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

List Dives
^^^^^^^^^^
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

Add Dive Site
^^^^^^^^^^^^^
The diver adds a dive site data to logbook file. The data can be

- id of dive site
- location, i.e. Red Sea
- name, i.e. SS Thistlegorm
- position (longitude and latitude) of dive site

List Dive Sites
^^^^^^^^^^^^^^^
The diver lists dive sites stored in logbook file.

Remove Dive Site
^^^^^^^^^^^^^^^^
The diver removes dive site data from logbook file.

Add Buddy
^^^^^^^^^
The diver adds a buddy data to logbook file. The data can be

- buddy id (short string like initials, nickname, etc.)
- name
- organization, i.e. PADI, CMAS
- member id of organization buddy belongs to

List Buddies
^^^^^^^^^^^^
The diver lists buddy data stored in logbook file.

Remove Buddy
^^^^^^^^^^^^
The diver removes buddy data from logbook file.

.. _hk-us-analysis:

Data Analysis
-------------
The analyst runs script to analyze dive and dive profile data. The script can
have arguments.

.. _planning:

Planning
--------

Simple Calculation
^^^^^^^^^^^^^^^^^^

.. vim: sw=4:et:ai
