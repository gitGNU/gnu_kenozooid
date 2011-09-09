Dive Calculators
================
Kenozooid's dive calculators can be useful for dive planning, when maximum
operating depth (MOD), equivalent air depth (EAD), respiratory minute
volume (RMV) or other information (i.e. PPO2) is required.

Calculator commands are grouped with ``calc`` word - invoke ``kz calc -h``
to list all calculators.

To calculate MOD when breathing EAN 32 (PPO2 1.4 by default)::

    $ kz calc mod 32
    33.75

To calculate MOD when breathing EAN 32 for PPO2 1.6::

    $ kz calc mod 1.6 32
    40.00

To calculate EAD for 30m when breating EAN 32::

    $ kz calc ead 30 32
    24.43

To calculate PPO2 for 30m when breathing EAN 32::

    $ kz calc ppO2 30 32
    1.28

To calculate RMV for a 55 minutes dive with average depth of 16.2m (15l
tank, 220bar - 50bar = 170bar used pressure)::

    $ kz calc rmv 15 170 16.2 55
    17.70

.. vim: sw=4:et:ai
