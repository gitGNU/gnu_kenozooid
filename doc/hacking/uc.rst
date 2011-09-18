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

+---------------+--------------+-------------------------------+---------------------+----------------+
| Diver         | UI           | Logbook                       | Driver              | Dive Computer  |
+===============+==============+===============================+=====================+================+
| Start backup. | Verify input | Identify dive computer and    | Request raw data.   | Send raw data. |
|               | parameters.  | find appropriate driver.      |                     |                |
+---------------+--------------+-------------------------------+---------------------+----------------+
|               |              |                               | Convert raw data to |                |
|               |              |                               | dive data.          |                |
+---------------+--------------+-------------------------------+---------------------+----------------+
|               |              | Create backup file.           |                     |                |
|               |              |                               |                     |                |
|               |              | Store raw data, dive data and |                     |                |
|               |              | dive computer information     |                     |                |
|               |              | into new backup file.         |                     |                |
|               |              |                               |                     |                |
|               |              | Reorder dives.                |                     |                |
|               |              |                               |                     |                |
|               |              | Save new backup file.         |                     |                |
+---------------+--------------+-------------------------------+---------------------+----------------+

Dive Computer Backup Reprocess
------------------------------
**Pre:** backup file exists

**Input:** new backup file name

+--------------+--------------+-------------------------------+---------------------+
| Diver        | UI           | Logbook                       | Driver              |
+==============+==============+===============================+=====================+
| Start backup | Verify input | Lookup dive computer original |                     |
| reprocess.   | parameters.  | data.                         |                     |
|              |              |                               |                     |
|              |              | Identify dive computer and    |                     |
|              |              | find dive computer driver.    |                     |
+--------------+--------------+-------------------------------+---------------------+
|              |              |                               | Convert raw data to |
|              |              |                               | dive data.          |
+--------------+--------------+-------------------------------+---------------------+
|              |              | Create backup file.           |                     |
|              |              |                               |                     |
|              |              | Store raw data, dive data and |                     |
|              |              | dive computer information     |                     |
|              |              | into new backup file.         |                     |
|              |              |                               |                     |
|              |              | Reorder dives.                |                     |
|              |              |                               |                     |
|              |              | Save new backup file.         |                     |
+--------------+--------------+-------------------------------+---------------------+


Convert Raw Dive Computer Data
------------------------------
**Pre:** file with raw dive computer data exists

**Input:** driver name, raw dive computer data, new backup file name

+-------------------+--------------+-------------------------------+---------------------+
| Diver             | UI           | Logbook                       | Driver              |
+===================+==============+===============================+=====================+
| Start conversion. | Verify input | Read raw data.                |                     |
|                   | parameters.  | data.                         |                     |
|                   |              |                               |                     |
|                   |              | Identify dive computer and    |                     |
|                   |              | find dive computer driver.    |                     |
+-------------------+--------------+-------------------------------+---------------------+
|                   |              |                               | Convert raw data to |
|                   |              |                               | dive data.          |
+-------------------+--------------+-------------------------------+---------------------+
|                   |              | Create backup file.           |                     |
|                   |              |                               |                     |
|                   |              | Store raw data, dive data and |                     |
|                   |              | dive computer information     |                     |
|                   |              | into new backup file.         |                     |
|                   |              |                               |                     |
|                   |              | Reorder dives.                |                     |
|                   |              |                               |                     |
|                   |              | Save new backup file.         |                     |
+-------------------+--------------+-------------------------------+---------------------+

.. _hk-uc-analysis:

Analyze Data
------------
**User Story**: :ref:`hk-us-analysis`

**Pre**: files with dive data exist and dives to analyze exist

**Input**: script, script arguments, names of files with dive data, dives
to analyze

Kenzooid integrates with R statistical package (analytics software) for
dive data analysis, therefore a "script" is R script.

A script can be provided by Kenozooid team and distributed with Kenozooid
or written by an analyst or other 3rd party. Locating is finding script
within Kenozooid directory structure (created due to installation) or
loading it using path specified by analyst.

It is up to the R script to present results of data analysis.

+-------------------+--------------+-------------------------------+----------------------+
| Analyst           | UI           | Analytics                     | Analytics software   |
+===================+==============+===============================+======================+
| Start data        | Verify input | Locate script.                | Execute R script.    |
| analysis.         | parameters.  |                               |                      |
|                   |              | Load dive data into R space.  |                      |
|                   |              |                               |                      |
|                   |              | Load script into R space.     |                      |
|                   |              |                               |                      |
|                   |              | Pass script arguments to      |                      |
|                   |              | R script.                     |                      |
|                   |              |                               |                      |
|                   |              | Start R script execution.     |                      |
+-------------------+--------------+-------------------------------+----------------------+

.. vim: sw=4:et:ai
