Dive Data Analysis
==================
For dive data analysis Kenozooid integrates with R, which is free software
environment for statistical computing and graphics. 

Kenozooids converts diving data stored in UDDF files into R data structures
and allows to execute R scripts to perform data analysis and plotting.

Several data anlysis scripts are provided by Kenozooid (see
:ref:`user-analysis-scripts`). For example, to calculate RMV::

    $ kz analyze rmv.R -a examples/rmv.csv 15 -k 19 dumps/ostc-dump-18.uddf

      time avg_depth avg_rmv
    1    4       5.5    48.4
    2    9       6.1    41.4
    3   17       6.3    32.5
    4   24       6.4    26.7


.. _user-analysis-scripts:

Data Analysis Scripts
---------------------
The list of data analysis scripts provided by Kenozooid is as follows

rmv.R
    calculate respiratory minute volume (RMV)

Respiratory Minute Volume (RMV)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Use ``rmv.R`` script to calculate respiratory minute volume (RMV).

The script accepts two parameters

csv file
    CSV file with two columns - ``time`` and ``pressure``. Time is dive run
    time in minutes and pressure is tank pressure in bars.
tank
    Size of tank in liters.

The output of the script is a table with columns

time
    Dive run time in minutes.
avg_depth
    Average dive depth.
avg_rmv
    Average RMV for running time and average depth.

For example, create ``dive-19-rmv.csv`` file::

    time,pressure
    0,210
    4,190
    9,170
    17,150
    24,140

Then execute ``rmv.R`` script for 15l tank::

    $ kz analyze rmv.R -a dive-19-rmv.csv 15 -k 19 dumps/ostc-dump-18.uddf

      time avg_depth avg_rmv
    1    4       5.5    48.4
    2    9       6.1    41.4
    3   17       6.3    32.5
    4   24       6.4    26.7

Custom Data Analysis Scripts
----------------------------
Custom data analysis scripts consist of three steps

- parse script arguments (optional)
- perform data analysis
- create analysis output

Kenozooid will deliver all dive data and script arguments to a script. The
data structures created by Kenozooid for a script are described in
:ref:`user-analysis-data`.

A script is responsible to deliver data analysis output, i.e. it should
print results on screen or create PDF files.

For example, create ``dhours.R`` script to summarize total amount of diving
hours::

    secs = sum(kz.dives$duration)
    print(sprintf('Total dive hours %.1f', secs / 3600))

Execute it with Kenozooid::

    $ kz analyze dhours.R examples/logbook.uddf

    [1] "Total dive hours 2.1"

.. _user-analysis-data:

Data Structures
^^^^^^^^^^^^^^^
The data available for analysis on R level can be accessed with ``kz``
object. The following data are provided by Kenozooid

``kz.args``
    List of script arguments passed from Kenozooid command line user
    interface.
``kz.dives``
    Data frame containing dive data.
``kz.profiles``
    Data frame containing dive profile data.

The data frame containig dive information has the following columns

``datetime``
    Date and time of a dive.
``depth``
    Maximum depth of dive in meters.
``duration``
    Dive duration in minutes.
``temp``
    Minimum dive temperature recorded during dive.

The data frame containig dive profile information has the following columns

``dive``
    Dive number to reference dive - row number in ``kz.dives`` data frame.
``depth``
    Depth during the dive.
``time``
    Dive time in seconds.
``temp``
    Temperature during the dive.
``deco_time``
    Time of deepest deco stop at given time of dive (deco ceiling length).
``deco_depth``
    Depth of deco stop at give time of dive (deco ceiling).
``gas_name``
    Name of gas mix switched at given depth.
``gas_o2``
    O2 percentage of switched gas mix.
``gas_he``
    Helium percentage of switched gas mix.
``mod_low``
    Maximum operating depth (MOD) for gas mix at 1.4 PPO2.
``mod_high``
    Maximum operating depth (MOD) for gas mix at 1.6 PPO2.

.. vim: sw=4:et:ai
