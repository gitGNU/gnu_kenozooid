Use Cases
=========

Manage Dive Computer Data
-------------------------

Dive Computer Backup
^^^^^^^^^^^^^^^^^^^^
**Pre:** dive computer is correctly connected

**Input:** dive computer, backup file name

+---------------+--------------+-------------------------------+---------------------+----------------+
| Diver         | UI           | Logbook                       | Drivers             | Dive Computer  |
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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**Pre:** backup file exists

**Input:** new backup file name

+--------------+--------------+-------------------------------+---------------------+
| Diver        | UI           | Logbook                       | Drivers             |
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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
**Pre:** file with raw dive computer data exists

**Input:** driver name, raw dive computer data, new backup file name

+-------------------+--------------+-------------------------------+---------------------+
| Diver             | UI           | Logbook                       | Drivers             |
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

Plot Dive Data
--------------
**User Story**: :ref:`hk-us-plot-dive-details`, :ref:`hk-us-plot-dive-cmp`

**Pre**: files with dive data exist and dives to plot exist

**Input**: names of files with dive data, dives to analyze

**Output**: output file name

The use case reuses :ref:`hk-uc-analysis` use case. Appropriate R script
is used for different types of plots described by user stories.

The extension of output file name defines the format of the output file.

Plan Dive
---------

Calculate
^^^^^^^^^
**User Story**: :ref:`hk-us-calc`

**Input**: calculator name, calculator parameters

**Output**: calculator's output

The diver uses a calculator for dive planning. There are several
calculators

- ppO2
- ppN2
- ead
- mod
- rmv

Each calculator has parameters (for example depth or gas mix), which has to
be provided by the diver.

+--------------------+------------------+------------+
| Diver              | UI               | Planning   |
+====================+==================+============+
| Start calculation. | Verify input     | Calculate. |
|                    | parameters.      |            |
|                    |                  |            |
|                    | Find calculator  |            |
|                    | function.        |            |
|                    |                  |            |
|                    |                  |            |
|                    |                  |            |
|                    |                  |            |
|                    |                  |            |
|                    |                  |            |
+--------------------+------------------+------------+
|                    | Output result of |            |
|                    | the calculation. |            |
+--------------------+------------------+------------+

Manage Logbook
--------------

Add Dive
^^^^^^^^
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

Upgrade File Format Version
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Pre:** input file exists and is valid file for previous version of file
format

**Output:** output file is valid file for new version of file format

**Input:** input file with dive data

**Output:** output file with dive data

The use case is about upgrading UDDF files to new version of the standard.

Upgrade path is determined as follows

- determine current version of input file
- find all next versions from current version till new version of file
  format

This way, multiple file format versions updating can be supported.

+--------------------+----------------------+----------------------------+
| Diver              | UI                   | Logbook                    |
+====================+======================+============================+
| Start upgrading.   | Verify input         | Find upgrade path.         |
|                    | parameters.          |                            |
|                    |                      | Upgrade file.              |
|                    | Rename input file as |                            |
|                    | backup file.         | Save file.                 |
+--------------------+----------------------+----------------------------+

.. vim: sw=4:et:ai
