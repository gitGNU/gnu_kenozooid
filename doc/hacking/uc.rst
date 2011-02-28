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

**Input:** basic dive data (date, maximum depth, duration)
or dive profile and profile file, logbook file;
optional dive data (time of dive, buddy, dive site)

+----------+--------------+----------------------------------------------------------+
| Diver    | UI           | Logbook                                                  |
+==========+==============+==========================================================+
| Add dive | Verify input | If dive profile provided then extract basic dive data.   |
|          | parameters   |                                                          |
|          |              | Insert basic and optional dive data into logbook file.   |
|          |              |                                                          |
|          |              | If dive profile provided                                 |
|          |              |                                                          |
|          |              | - insert dive profile data                               |
|          |              | - copy any additional data associated with profile       |
|          |              |   data (i.e. equipment used)                             |
+----------+--------------+----------------------------------------------------------+

Dive Computer Backup
--------------------

**Pre:** dive computer is correctly connected

**Input:** dive computer, backup file

+--------------+--------------+---------------------------+-------------------------+---------------+
| Diver        | UI           | Logbook                   | Driver                  | Dive Computer |
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
