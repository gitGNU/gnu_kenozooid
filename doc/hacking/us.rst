.. _hk-us:

User Stories
============

.. _hk-us-dc:

Dive Computer
-------------

.. _hk-us-backup:

Backup
^^^^^^
The diver backups dive computer data - configuration and dive profiles.

Dive computer data in its original (highly probably binary) structure is
saved, then processed to Kenozooid data structures and saved. See also
:ref:`hk-us-rbackup`.

.. _hk-us-rbackup:

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

.. _hk-us-sim-plan:

Dive Plan Simulation
^^^^^^^^^^^^^^^^^^^^
Some of the dive computers allow to enter dive mode and simulate a dive
with dive computer buttons, by controlling it from a personal computer or
by using both techniques.

The diver starts simulation on a dive computer from a personal computer
to simulate a dive plan.

.. _hk-us-sim-replay:

Dive Replay
^^^^^^^^^^^
The diver starts dive simulation on a dive computer from a personal
computer to replay a dive profile stored in dive logbook.

.. _hk-us-plotting:

Data Plotting
-------------

.. _hk-us-plot-dive-details:

Plot Dive Profile Details
^^^^^^^^^^^^^^^^^^^^^^^^^
The diver creates plots of multiple dive profiles.

Each dive profile plot is in separate file (or on separate page, i.e. in
case of PDF file). The supported file output formats shall be: PDF, SVG and
PNG.

Each plot contains the following information

- dive profile graph (time vs. depth)
- title (optional)
- dive information (optional)

  - duration
  - maximum depth
  - temperature

- average depth line (optional)
- deco ceiling graph
- gas change
- setpoint change
- 1.4 and 1.6 ppO2 depth limit graph (optional)
- maximum ascent and descent events (optional)

Ascent speed values

- are prefixed with "+"
- visible when greater than 10m/min

Descent speed values

- are prefixed with "-"
- visible when greater than 20m/min

.. _hk-us-plot-dive-cmp:

Compare Dive Profiles
^^^^^^^^^^^^^^^^^^^^^
The diver creates plot to compare two or more dive profiles.

The plot contains the following information

- graph of dive profiles (each profile with different color)
- title (optional)

.. _hk-us-analysis:

Data Analysis
-------------
The analyst runs script to analyze dive and dive profile data. The script can
have arguments.

.. _hk-us-planning:

Planning
--------

.. _hk-us-calc:

Simple Calculation
^^^^^^^^^^^^^^^^^^
The diver calculates

- O2 partial pressure (ppO2) for depth and gas mix
- Nitrogen parital pressure (ppN2) for depth and gas mix
- equivalent air depth (EAD) for depth and gas mix
- maximum operating depth (MOD) for ppO2 and gas mix
- respiratory minute volume (RMV) for tank size, pressure in tank, maximum
  depth and dive duration

.. _hk-us-plan-deco:

Decompression Dive
^^^^^^^^^^^^^^^^^^
The diver is planning a decompression dive.

The dive plan input is

- gas mix list (each with optional gas mix switch)

  - travel gas mixes (0 or more)
  - bottom gas mix
  - decompression gas mixes (0 or more)

- maximum dive depth
- bottom time
.. not for ver. 0.15: - diving cylinders specification (optional)

Kenozooid calculates dive plan, which consists of

- main dive profile summary

  - maximum dive depth
  - bottom time (includes descent time)
  - descent time
  - total decompression time
  - total dive time

- emergency dive profile summary for lost gas
- emergency dive profile summary for extended dive profile
- emergency dive profile summary for extended dive profile and lost gas

- gas logistics information

  - volume of each required gas mix for the main dive profile calculated
    using rule of thirds
  - volume of each required gas mix for each emergency dive profile
.. not for ver. 0.15: - verification message that volume of each gas mix fits into specified,
.. not for ver. 0.15:   appropriate diving cylinder, warning otherwise (if diving cylinder
.. not for ver. 0.15:   configuration specified)

- dive slates for

  - planned dive profile
  - emergency lost gas dive profile
  - emergency extended dive profile
  - emergency extended dive profile and lost gas

Decompression stops are calculated with a decompression engine library.

Dive slate consists of the following columns

- depth (is prefixed with `*` character on gas mix change event)
- decompression time
- run time
- gas mix used at given dive profile segment

The dive plan is shown on the screen in textual format compatible with
reStructuredText standard.

.. not for ver. 0.15: or can be saved as PDF file for printing.

The dive plan should be configurable with

- last stop 3m or 6m; default 3m
- gradient factors; default GF low 30%, GF high 85%
- respiratory minute volume (RMV); default 20l/min

The following parameters are used for dive plan calculation and might be
configurable in the future

- descent rate 20m/min
- extended dive profile is 5 meters deeper and 3 minutes longer (+5m/+3min)
- decompression model is ZH-L16B-GF
- travel and bottom gas mix switch depth is calculated using ppO2 1.4
- bottom gas mix switch depth is calculated using ppO2 1.6
- decompression engine library is ``decotengu``

.. not for ver. 0.15: - travel and decompression gas mixes cylinders pressure 200bar
.. not for ver. 0.15: - bottom gas mix cylinder pressure 220bar

.. _hk-us-logbook:

Logbook
-------

.. _hk-us-adddive:

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

.. _hk-us-copydive:

Copy Dives
^^^^^^^^^^
The diver copies dive from dive data backup or dive logbook to another
dive logbook.

List Dives
^^^^^^^^^^
The diver lists dives from dive logbook.

By default, all dives are displayed.

The dives output can be limited with

- dive date query
- buddy
- dive site

.. _hk-us-enumdives:

Enumerate Dives
^^^^^^^^^^^^^^^
The diver enumerates dives in dive logbook.

The dives are enumerated in two ways

- total dive number
- day dive number

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

Upgrade Files
^^^^^^^^^^^^^
The file format standard used by Kenozooid changes with time. The diver
wants to upgrade his files to newer version of the file format. 

.. vim: sw=4:et:ai
