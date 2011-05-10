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
**Input:** dive data (date, maximum depth, duration) or dive profile in
profile file, logbook file; optional dive data (time of dive, minimum
temperature, buddy, dive site)

The use case is about storing dive information in dive logbook - while dive data
like duration or maximum depth is extracted (or calculated) from some dive
profile (i.e. contained in dive computer backup file), then the types of data
being copied is strictly limited below. Data copying functionality could be
provided by other use case (if ever).

Data, which can be extracted (calculated) from dive profile

- date and time of dive
- maximum depth
- duration
- minimum temperature
- information about dive computer used to obtain dive profile

Data, which *cannot* be extracted from dive profile

- buddy
- dive site

+-----------+--------------+----------------------------------------------------+
| Diver     | UI           | Logbook                                            |
+===========+==============+====================================================+
| Add dive. | Verify input | Open logbook file (create if necessary).           |
|           | parameters.  |                                                    |
|           |              | If dive profile provided, then extract appropriate |
|           |              | dive data from dive profile.                       |
|           |              |                                                    |
|           |              | Insert dive data into logbook file.                |
|           |              |                                                    |
|           |              | If dive profile provided, then insert into logbook |
|           |              | file.                                              |
|           |              |                                                    |
|           |              | - dive profile data                                |
|           |              | - used dive computer information if available      |
|           |              |                                                    |
|           |              | Reorder dives.                                     |
|           |              |                                                    |
|           |              | Save logbook file.                                 |
+-----------+--------------+----------------------------------------------------+

Dive Computer Backup
--------------------
**Pre:** dive computer is correctly connected

**Input:** dive computer, backup file name

+---------------+--------------+----------------------------+-------------------------+----------------+
| Diver         | UI           | Logbook                    | Driver                  | Dive Computer  |
+===============+==============+============================+=========================+================+
| Start backup. | Verify input | Identify dive computer and |                         |                |
|               | parameters.  | find appropriate driver.   |                         |                |
+---------------+--------------+----------------------------+-------------------------+----------------+
|               |              | Create backup file.        | Request raw data.       | Send raw data. |
+---------------+--------------+----------------------------+-------------------------+----------------+
|               |              | Store raw data in backup   | Convert raw data to     |                |
|               |              | file.                      | universal data model.   |                |
+---------------+--------------+----------------------------+-------------------------+----------------+
|               |              | Store universal data       |                         |                |
|               |              | in backup file including   |                         |                |
|               |              | dive computer information. |                         |                |
|               |              |                            |                         |                |
|               |              | Reorder dives.             |                         |                |
|               |              |                            |                         |                |
|               |              | Save backup file.          |                         |                |
+---------------+--------------+----------------------------+-------------------------+----------------+

Dive Computer Backup Reprocess
------------------------------
**Pre:** backup file exists

**Input:** new backup file name

+--------------+--------------+-------------------------------+-------------------------+
| Diver        | UI           | Logbook                       | Driver                  |
+==============+==============+===============================+=========================+
| Start backup | Verify input | Lookup dive computer original |                         |
| reprocess.   | parameters.  | data.                         |                         |
|              |              |                               |                         |
|              |              | Identify dive computer and    |                         |
|              |              | find dive computer driver.    |                         |
|              |              |                               |                         |
|              |              | Create backup file.           |                         |
|              |              |                               |                         |
|              |              | Store raw data in new backup  |                         |
|              |              | file.                         |                         |
+--------------+--------------+-------------------------------+-------------------------+
|              |              |                               | Convert raw data to     |
|              |              |                               | universal data model.   |
+--------------+--------------+-------------------------------+-------------------------+
|              |              | Store universal data          |                         |
|              |              | in new backup file including  |                         |
|              |              | dive computer information.    |                         |
|              |              |                               |                         |
|              |              | Reorder dives.                |                         |
|              |              |                               |                         |
|              |              | Save new backup file.         |                         |
+--------------+--------------+-------------------------------+-------------------------+

.. vim: sw=4:et:ai