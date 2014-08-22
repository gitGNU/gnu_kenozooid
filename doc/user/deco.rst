Decompression Dive Plan
=======================
The ``plan deco`` Kenozooid command enables diver to plan a decompression
dive.

For example. to plan decompression dive to 42 meters, for 25 minutes, EAN27
bottom gas mix, EAN50 decompression gas mix and last decompression stop at
6m use command::

    $ kz plan deco -6 'ean27 ean50@22' 42 25

Dive Plan Input
---------------
Dive plan input requires three mandatory arguments

- gas mix list
- dive maximum depth in meters
- bottom time in minutes

The dive maximum depth and bottom time arguments shall require no
explanation.

The gas mix list is space separated list of gas mix names

- optional travel gas mix
- mandatory bottom gas mix
- optional decompression gas mix

The gas mix name is case insensitive and can be

air
    Air gas mix, set to 21% oxygen and 79% nitrogen.
o2
    Gas mix with 100% oxygen.
eanOO
    Nitrox gas mix with `OO` oxygen percentage, for example `EAN27`, `EAN50`.
txOO/HE
    Trimix gas mix  with `OO` oxygen percentage and `HE` helium percentage,
    for example `TX21/35`, `TX18/45`, `TX15/55`.

To specify gas mix switch depth with its name add `@D` suffix where `D` is
the depth, for example `EAN50@22` is gas mix to be switched to at 22
meters.

Travel gas mix name has `+` prefix, for example `+EAN32@0` or `+EAN32` is
EAN32 travel gas mix to be used from surface.

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
