Introduction
============
Kenozooid is software used to plan and analyse diving activities. Features
like dive data plotting and analysis, dive computer support along with
simple but powerful logbook maintenance and dive calculators are already
implemented with further functions such as dive planning to come.

Kenozooid is free software licensed under terms of
`GPL <http://www.fsf.org/licensing/licenses/gpl.html>`_ license.

Features
--------
Kenozooid is under heavy development, but following features are already
implemented

- high quality dive data plotting using `R <http://www.r-project.org/>`_
  statistical software

    - one plot per page
    - overlay of multiple plots on one graph
    - configurable (title on/off, legend on/off, plot labels, dive
      information on/off, temperature graph on/off)
    - PDF, SVG and PNG are supported formats

- dive data analysis using `R <http://www.r-project.org/>`_
  statistical software
- ppO2, ppN2, EAD and MOD calculators
- logbook management

    - dives listing, searching, adding and removal
    - dive sites listing, searching, adding and removal
    - buddies listing, searching, adding and removal

- dive computers support

    - dive data fetching
    - execution of dive simulation using dive computers providing such
      capabilities
    - backup of dive computer data
    - regeneration of dive data from backup to improve and fix data in case
      of new Kenozooid capabilities and bug fixes

- drivers for following devices are implemented

    - open source OSTC based dive computers (OSTC, Mk.2, N2) by
      `HeinrichsWeikamp GbR <http://www.heinrichsweikamp.net/>`_
    - Sensus Ultra by `ReefNet Inc. <http://reefnet.ca/products/sensus/>`_
    - dummy device driver displaying information to standard output

- neat and powerful command line user interface
- native UDDF file format support (implies built-in interoperability
  with other applications)

Planned Features
----------------
New dive computer drivers can be added on request if a dive computer
is supported by `Libdivecomputer <http://www.divesoftware.org/libdc/>`_
library.

At least two different dive planning algorithms will be implemented

- `ratio deco <http://en.wikipedia.org/wiki/Ratio_decompression>`_
  schedules calculation 
- integration with `OSTC or DR5 <http://www.heinrichsweikamp.net/>`_
  source code to calculate dive plan based on Buhlmann GF decompression
  algorithm 

.. vim: sw=4:et:ai
