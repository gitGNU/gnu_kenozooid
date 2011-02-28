Actors and Subsystems
=====================

Actors
------
The following Kenozooid actors are identified
    
dive computer
    A device storing dive data, i.e. dive computer, dive logger, etc.
    Dive computer is connectable to computer running Kenozooid software.
diver
    A diving person, who is interested in dive planning, logging and
    analysis.
statistical software
    Software to perform statistical analysis.

Subsystems
----------
Kenozoid consists of the following subsystems

analytics
    Analytics modules and statistical software integration.
drivers
    Device drivers allowing other subsystems to communicate with dive
    computers.
logbook
    Dive logging functionality. Buddy and dive site management.
planning
    Dive planning related activities. Includes calculators (i.e. EAD, MOD)
    and dive simulation (i.e. with dive computer).
UI
    Command line user interface allowing diver to access Kenozooid
    functionality.

Use Cases
=========

Add Dive
--------

Dive Computer Backup
--------------------

**Pre:** dive computer is correctly connected
**Input:** dive computer, backup file

+--------------+--------------+---------------------------+-------------------------+---------------+
| Diver        | UI           | Logbook                   | Drivers                 | Dive Computer |
+==============+==============+===========================+=========================+===============+
| Start backup | Verify input |                           | Identify dive computer  |               |
|              | parameters   |                           | and provide appropriate |               |
|              |              |                           | driver                  |               |
+--------------+--------------+---------------------------+-------------------------+---------------+
|              |              | Create backup file        | Request raw data        | Send raw data |
+--------------+--------------+---------------------------+-------------------------+---------------+
|              |              | Store raw data in         | Convert raw data to     |               |
|              |              | backup file               | universal data model    |               |
+--------------+--------------+---------------------------+-------------------------+---------------+
|              |              | Store universal data      |                         |               |
|              |              | in backup file including  |                         |               |
|              |              | dive computer information |                         |               |
+--------------+--------------+---------------------------+-------------------------+---------------+
|              |              | Save backup file          |                         |               |
+--------------+--------------+---------------------------+-------------------------+---------------+

.. vim: sw=4:et:ai
