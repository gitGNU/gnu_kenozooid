Actors and Subsystems
=====================

Actors
------
The following Kenozooid actors are identified
    
analyst
    Data anylyst running a code (script) to analyze dive data.
dive computer
    A device storing dive data, i.e. dive computer, dive logger, etc.
    Dive computer is connectable to computer running Kenozooid software.
diver
    A diving person, who is interested in dive planning, logging and
    analysis.
analytics software
    Software to perform dive data analysis.

Subsystems
----------
Kenozoid consists of the following subsystems

analytics
    Analytics modules and statistical software integration.
drivers
    Device drivers allowing other subsystems to communicate with dive
    computers. Device drivers should not interpolate any data (i.e. missing
    temperature values).
logbook
    Dive logging functionality. Buddy and dive site management.
planning
    Dive planning related activities. Includes calculators (i.e. EAD, MOD)
    and dive simulation (i.e. with dive computer).
UI
    Command line user interface allowing actors to access Kenozooid
    functionality.

.. vim: sw=4:et:ai
