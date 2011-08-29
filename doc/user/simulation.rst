.. _dc-simulation:

Dive Simulation
---------------

Ability to perform dive simulation implemented in some of dive computers
can be great tool to familiarize yourself with computer screens and
features present during diving.

Kenozooid supports switching dive computers into simulation mode using
``sim plan`` and ``sim replay`` commands. The commands supply dive
computer with depth values in intervals of time. The depths and time
intervals can be generated from a dive plan (``sim plan``) or taken from an
existing dive profile (``sim replay``).

It is worth noting that real time dive simulation is described in this
section, therefore real life rules may apply to some of dive computers, for
example

- when dive is started, then computer switches into dive mode at
  appropriate depth; it depends on dive computer configuration
- when you reach surface, then computer may wait some time before exiting
  dive mode, if another simulation is started too fast, then it is counted
  as one dive

Please, read about dive simulation capabilities in your dive computer
manual before starting to use Kenozooid to simulate dives.

Dive Replay
^^^^^^^^^^^
Existing dive profile can be replayed with a dive computer having dive
simulation capabilities, i.e. OSTC. Kenozooid supports such functionality
with ``sim replay`` command.

To replay first dive from a backup file::

    kz sim replay ostc /dev/ttyUSB0 1 backup-ostc-20090214.uddf

Dive Plan Simulation
^^^^^^^^^^^^^^^^^^^^
Simulation of a dive plan is performed using ``sim plan`` command.

Sample dive plan could be as follows

+----------+-------+
| Run Time | Depth |
+==========+=======+
|     0:30 |    10 |
+----------+-------+
|     3:30 |    10 |
+----------+-------+
|    13:30 |     0 |
+----------+-------+

which can be described as

- dive starts at zero meters
- within 30 seconds diver reaches 10m
- diver stays at 10m for 3 minutes (leaves 10m at 3:30)
- then goes to the surface with 10m/min speed
- finally reaches surface at 13:30

To perform simulation of above dive plan with OSTC dive computer::

    kz sim plan ostc /dev/ttyUSB0 '0:30,10 3:30,10 13:30,0'

Dive specification is space separated list of dive run times and depth
values. 

Time can be specified in seconds (i.e. 15, 20, 3600) or in minutes (i.e.
12:20, 14:00, 67:13). Depth is always specified in meters.

Partial Automatic Simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Kenozooid allows not only to execute end-to-end simulation (start from
surface, perform dive, finish at surface) but as well part of simulation,
i.e. start simulation, dive to some depth starting from surface and exit
Kenozooid leaving dive computer in simulation mode to allow a diver to
continue simulation using dive computer buttons.

To support such flexiblity, two options are provided 

- no start option allows to start Kenozooid without restarting dive
  simulation
- no stop option leaves dive simulation running on Kenozooid exit

For example, to leave dive computer at 10m depth and then continue
simulation with dive computer buttons::

    kz --no-stop sim plan ostc /dev/ttyUSB0 '0:30,10'

Above simulation can be continued manually or it can be stopped using
Kenozooid::

    kz --no-start sim plan ostc /dev/ttyUSB0 '0,10 1:00,0'

To execute part of dive plan, no start and no stop options can be used at
once. For example, to ascend from 30m to 20m within 2 minutes::

    kz --no-start --no-stop sim plan ostc /dev/ttyUSB0 '0,30 120,20'

All times are run times from the moment, when Kenozooid is started.

.. vim: sw=4:et:ai
