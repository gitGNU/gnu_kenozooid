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

Simulation
^^^^^^^^^^

.. _logbook:

Logbook
-------

.. _adddive:

Adding Dive
^^^^^^^^^^^
The diver adds a dive to dive logbook. A dive consists of a minimum of

- date
- maximum depth in meters
- duration in minutes

Optionally, a diver might provide any of

- time of dive
- buddy
- dive site

.. _adddivep:

Adding Dive With Profile
^^^^^^^^^^^^^^^^^^^^^^^^
The diver adds a dive with profile data to dive logbook. The minimal set of
data is obtained from the profile data.

The optional data can be added as in adddive_.

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
