.. _user-ui:

User Interface
==============
The Kenozooid functionality is accessed with command line user interface.
While it is powerful for some, it might be scary for others. Kenozooid
authors try to alleviate this fear by making the user interface as
consistent as possible. The description of its basics and principles can be
found in following paragraphs.

The ``kz`` script is used to execute Kenozooid commands, i.e. ``backup``,
``plot``, ``dive list`` or ``buddy add`` (some commands consist of two
words separated by space).

Start by typing ``kz`` to get brief list of commands::

    $ kz
    usage: kz [-h] [-v]
              {analyze,backup,buddy,calc,convert,dive,drivers,plot,sim,site} ...
    kz: error: too few arguments


To get brief list of dive data related commands simply type::

    $ kz dive
    usage: kz dive [-h] {add,extract,list} ...
    kz dive: error: too few arguments

Use ``-h`` option to get more detailed overview of commands::

    $ kz dive -h
    usage: kz dive [-h] {add,extract,list} ...

    optional arguments:
      -h, --help          show this help message and exit

    Kenozooid dive management commands:
      {add,extract,list}
        add               add dive to UDDF file
        extract           extract dives from dive computer backup
        list              list dives stored in UDDF file

Common Options
--------------
Kenozooid ``kz`` script has  set of common options supported by each
command

\-h, --help
    Print command detailed overview.

\-v, --verbose
    Print debugging information. The information should be sent to
    Kenozooid authors when reporting problems.

.. vim: sw=4:et:ai
