Dive Data Analysis
==================
For dive data analysis Kenozooid integrates with R, which is free software
environment for statistical computing and graphics. 

Kenozooids converts diving data stored in UDDF files into R data structures
and allows to execute R scripts to perform data analysis and plotting.

Several data anlysis scripts are provided by Kenozooid (see
:ref:`user-analysis-scripts`). For example, to calculate RMV::

    $ kz analyze rmv.R -a examples/rmv.csv -- 19 dumps/ostc-dump-18.uddf
      time    depth      rmv
    1  240 5.484000 48.43710
    2  540 6.596774 36.15160
    3 1020 6.534694 22.67959
    4 1440 6.632558 12.88351

.. _user-analysis-scripts:

Data Analysis Scripts
---------------------

Custom Data Analysis Scripts
----------------------------
Data Structures
^^^^^^^^^^^^^^^
The data available for analysis on R level can be accessed with ``kz``
object. The following data are provided by Kenozooid

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
``time``
    Dive time in seconds.
``depth``
    Depth during the dive.
``temp``
    Temperature during the dive.
``deco_time``
    Time of deepest deco stop at given time of dive (deco ceiling length).
``deco_depth``
    Depth of deco stop at give time of dive (deco ceiling).

.. vim: sw=4:et:ai
