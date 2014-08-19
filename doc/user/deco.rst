Decompression Dive Plan
=======================
The ``plan deco`` Kenozooid command enables diver to plan a decompression
dive.

Example::

    $ kz plan deco -6 -gl 20 -gh 90  'ean27 ean50@22' 42 25

Dive Plan Input
---------------

Dive Plan Overview
------------------

A decompression dive plan consists of

- dive plan summary
- gas mix logistics information
- dive slates
- dive plan parameters

The plan is prepared for planned dive profile and three emergency
situations, which gives four dive profiles in total

P
    Planned dive profile.
E
    Emergency dive profile for extended dive situation, this is deeper and
    longer dive. By default, extended dive profile is 5m deeper and 3 minutes
    longer.
LG
    Emergency dive profile for lost decompression gas situation.
E+LG
    Emergency dive profile for both extended and lost decompression gas
    situations.

Example of dive plan summary

============================== ====== ====== ====== ======
 Name                            P      E      LG    E+LG
============================== ====== ====== ====== ======
============================== ====== ====== ====== ======

Dive Slates
-----------
Kenozooid creates a dive slate for each dive profile, which consists of
four columns

D
    Dive depth [meter]. The depth is prefixed with ``*`` on gas mix change
    at given depth.
DT
    Decompression stop time [min].
RT
    Dive run time [min].
GAS
    Gas mix information.

The dive slates can be written down or printed, then laminated and with
added bungee can be put on diver's forearm.

Example of dive slate for planned dive profile::

       D  DT   RT GAS
    ------------------------


Gas Mix Logistics
-----------------
Example of gas mix logistics information

============================== ====== ====== ====== ======
Gas Mix                          P      E      LG    E+LG
============================== ====== ====== ====== ======
============================== ====== ====== ====== ======

.. vim: sw=4:et:ai
