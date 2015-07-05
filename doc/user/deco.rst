Decompression Dive Plan
=======================
Decompression dive planning in Kenozooid is supported with the
``plan deco`` command.

For example, to plan decompression dive

- with EAN27 bottom gas mix
- with EAN50 decompression gas mix
- to maximum depth of 42 meters
- for 25 minutes

use command::

    $ kz plan deco 'ean27 ean50' 42 25

To change the dive plan parameters to

- respiratory volume minute 16l/min (default 20l/min)
- gradient factors low 20% and high 90% (default 30% and 85%)
- last decompression stop at 6m (default 3m)

we can use the command::

    $ kz plan deco --rmv 16 -gl 20 -gh 90 -6 'ean27 ean50' 42 25

or to specify gas mix switch depth in explicit way::

    $ kz plan deco --rmv 16 -gl 20 -gh 90 -6 'ean27@0 ean50@22' 42 25

Decompression dive plan generated with above command is

.. literalinclude:: deco-plan.txt
   :language: rst

The dive plan output is in `reStructuredText format <http://docutils.sourceforge.net/rst.html>`_
and can be simply printed or converted to many formats like PDF or HTML.

The decompression dive plan input and the details of its output are
discussed in the following sections.

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
LG
    Emergency dive profile for lost decompression gas situation.
E
    Emergency dive profile for extended dive situation, this is deeper and
    longer dive. By default, extended dive profile is 5m deeper and 3 minutes
    longer.
E+LG
    Emergency dive profile for both extended and lost decompression gas
    situations.

Example of dive plan summary

============================== ====== ====== ====== ======
 Name                            P      LG     E     E+LG
============================== ====== ====== ====== ======
Depth [m]                          42     42     47     47
Bottom Time [min]                  25     25     28     28
Descent Time [min]                2.1    2.1    2.4    2.4
Total Decompression Time [min]     14     20     25     38
Total Dive Time [min]              41     47     56     69
O2 Pressure of Bottom Gas Mix    1.40   1.40   1.54   1.54
MOD for Bottom Gas Mix             42     42     42     42
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
    * 42       25 EAN27
    * 22       27 EAN50
      18   1   28
      15   1   30
      12   1   31
       9   1   32
       6   8   41
       0       41

Gas Mix Logistics
-----------------
Gas mix logistics information provides diver with volume of each gas mix
required during each of dive profiles of a decompression dive. The volume
is calculated using 20l/min respiratory minute volume (RMV) by default and
is expressed in liters.

The gas mix volume for planned dive profile is calculated using rule of
thirds. For example, if 2000 liters of bottom gas mix is to be consumed by
a diver during planned dive profile, then dive cylinder setup holding 3000 liters
of the gas mix is required.

Having gas mix volume value, we can calculate if diving cylinder setup is
sufficient for a dive. For example, if 1600 liters of decompression gas mix
is required and we have choice of using 7 liter or 10 liter cylinder, then
we can calculate required pressure in each cylinder::

    1600 / 7  = 229
    1600 / 10 = 160

and we should decide to take 10 liter cylinder for the dive.

*NOTE:* The emergency dive profiles gas mix volume information is
calculated as is, this is *without* rule of thirds.

Example of gas mix logistics information

============================== ====== ====== ====== ======
Gas Mix                          P      LG     E     E+LG
============================== ====== ====== ====== ======
Gas Mix EAN27 [liter]            3216   2731   2703   3764
Gas Mix EAN50 [liter]             644   xx      709   xx
============================== ====== ====== ====== ======

Above example shows that we need at least 3216 liters of EAN27 for planned
dive profile (we will consume 2144 liters of gas mix). For any emergency
dive profile we need no more than 3764 liters of the gas mix.

.. vim: sw=4:et:ai
