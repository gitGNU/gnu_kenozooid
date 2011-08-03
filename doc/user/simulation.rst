Dive Simulation
---------------

Ability to perform dive simulation implemented in some of dive computers
can be great tool to familiarize yourself with computer screens and
features present during diving.

Kenozooid supports switching dive computers into simulation mode using
``simulate`` command. The command is used to supply dive computer with
depths for some period of time. Different scenarios can be performed

- end-to-end simulation (start from surface, perform dive, finish
  at surface)

- part of simulation, i.e. start simulation, dive to some depth starting
  from surface and exit leaving dive computer in simulation mode

Please note, this is real time dive simulation, therefore real life rules
may apply to some of dive computers

- when dive is started, then computer switches into dive mode at
  appropriate depth; it depends on dive computer configuration
- when you reach surface, then computer may wait some time before exiting
  dive mode, if another simulation is started too fast, then it is counted
  as one dive

Please, read about dive simulation capabilities in your dive computer
manual before starting to use Kenozooid software to simulate dives.

Performing Simulation
~~~~~~~~~~~~~~~~~~~~~
Dive simulation is performed using ``simulate`` command. There are two
parameters required

- device id
- dive plan specification

Sample dive plan could be described as follows

- dive starts at zero meters
- within 30 seconds diver reaches 10m
- diver stays at 10m for 3 minutes
- then reaches the surface with 10m/min. speed

To perform above dive simulation with OSTC dive computer the command should
be used::

    kenozooid simulate ostc '0:30,10 3:30,10 13:30,0'

Dive specification is space separated list of dive time and depth values. 

Time can be specified in seconds (i.e. 15, 20, 3600) or in minutes (i.e.
12:20, 14:00, 67:13). Depth is always specified in meters.

Continuing Simulation
~~~~~~~~~~~~~~~~~~~~~
Dive simulation can be executed in mixed manner. For example, it can be
started with aid of a (non-dive) computer and then performed manually using
dive computer buttons.

To support such flexiblity, two options are provided 

- no start option allows to start Kenozooid without restarting dive
  simulation
- no stop option leaves dive simulation running on Kenozooid exit

For example, to leave dive computer at 10m depth and then continue
simulation with dive computer buttons::

    kenozooid --no-stop simulate ostc '0:30,10'

Above simulation can be continued manually or it can be stopped using
Kenozooid::

    kenozooid --no-start simulate ostc '0,10 1:00,0'

To execute part of dive plan, no start and no stop options can be used at
once. For example, to ascend from 30m to 20m within 2 minutes::

    kenozooid --no-start --no-stop simulate ostc '0,30 120,20'

.. vim: sw=4:et:ai
