Introduction
============
Kenozooid is software used to plan and analyse diving activities. Features
like statistical analysis, dive profile plotting, dive computer support
along with simple but powerful logbook maintenance and dive calculators are
already implemented with further functions such as dive planning to come.

The project allows to process data stored by dive computers and utilize
their features like dumping dive computer memory, fetching dive log
information or performing dive simulation. 

Kenozooid can be used as a library for other dive related software
including dive logbook management applications, see :ref:`part-devel`
for more information.

Kenozooid is free software licensed under terms of
`GPL <http://www.fsf.org/licensing/licenses/gpl.html>`_ license.

Features
--------
Kenozooid is under development but following features are already present

- supported devices 
    - open source OSTC dive computer by HeinrichsWeikamp GbR,
      http://www.heinrichsweikamp.net/ostc/en/
    - dummy device driver displaying information to standard output
- device drivers can implement different capabilities, i.e. one dive
  computer can provide dive logbook data and allows to enter simulation
  mode, but other dive computer allows to fetch dive logbook only
- list available dive computers drivers and their capabilities
- scan for attached dive computers

Depending on dive computer driver capabilities

- enter dive simulation mode and send dive plan of dive simulation to
  a dive computer
- dumping dive computer memory into file

Planned Features
----------------
Kenozooid development is driven by features of owned dive computers, access
to hardware documentation and dive computer communication protocols
openess. 

Currently planned features are

- fetch dive logbook data for dives made in specified period of time
  (using *ostc* driver)
- create a dive graph
- support for ReefNet's Sensus Ultra dive data logger using libdivecomputer
  library

