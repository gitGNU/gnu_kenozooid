Requiremnts and Installation
============================

Requirements
------------

The table below describes Kenozooid core (mandatory) and optional dependencies.

The availability column provides information about a package being provided with an
operating system (i.e. Linux distro, FreeBSD) or a binary available to install on given
platform (Windows, Mac OS X).

+-----------------+----------+-------------+--------------------------+----------------------------+
|    Name         | Version  | Type        |  Availability            |  Description               |
+=================+==========+=============+==========================+============================+
|                                             **Core**                                             |
+-----------------+----------+-------------+--------------------------+----------------------------+
| Python          |   3.2    | execution   | Arch, Debian Wheezy,     | Kenozooid is written       |
|                 |          | environment | Fedora 15, Mac OS X,     | in Python language         |
|                 |          |             | PLD Linux, Ubuntu Natty, |                            |
|                 |          |             | Windows                  |                            |
+-----------------+----------+-------------+--------------------------+----------------------------+
| dateutil        |   2.0    | Python      | Mac OS X, PLD Linux,     | date and time parsing      |
|                 |          | module      | Windows                  |                            |
+-----------------+----------+-------------+--------------------------+----------------------------+
| lxml            |   2.3    | Python      | Fedora 15, Mac OS X,     | XML parsing and searching  |
|                 |          | module      | PLD Linux, Windows       |                            |
+-----------------+----------+-------------+--------------------------+----------------------------+
|                                           **Optional**                                           |
+-----------------+----------+-------------+--------------------------+----------------------------+
| pyserial        |    2.5   | Python      | PLD Linux, Windows       | required by OSTC driver    |
|                 |          | module      |                          |                            |
+-----------------+----------+-------------+--------------------------+----------------------------+
| libdivecomputer |          | library     |                          | required by Sensus Ultra   |
|                 |          |             |                          | driver                     |
+-----------------+----------+-------------+--------------------------+----------------------------+
| R               |  2.13.0  | Python      | Arch, Debian Wheezy,     | plotting and statistical   |
|                 |          | module      | Fedora 15, Mac OS X,     | analysis                   |
|                 |          |             | PLD Linux, Ubuntu Natty, |                            |
|                 |          |             | Windows                  |                            |
+-----------------+----------+-------------+--------------------------+----------------------------+
| rpy             |  2.2.2   | Python      | PLD Linux                | used to communicate with R |
|                 |          | module      |                          |                            |
+-----------------+----------+-------------+--------------------------+----------------------------+
| Hmisc           |          | R package   |                          | used for plotting          |
+-----------------+----------+-------------+--------------------------+----------------------------+

Installation
------------

Kenozooid Installation
~~~~~~~~~~~~~~~~~~~~~~

Python Modules
~~~~~~~~~~~~~~

R Packages
~~~~~~~~~~

.. vim: sw=4:et:ai
