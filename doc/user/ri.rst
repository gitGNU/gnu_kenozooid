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
| R               |  2.13.0  | R scripts   | Arch, Debian Wheezy,     | plotting and statistical   |
|                 |          | execution   | Fedora 15, Mac OS X,     | analysis                   |
|                 |          | environment | PLD Linux, Ubuntu Natty, |                            |
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
^^^^^^^^^^^^^^^^^^^^^^
At the moment Kenozooid is not released yet. In the future it will be possible to install
Kenozooid from `PyPI <http://pypi.python.org/pypi>`_, but at the moment it can be used
only by fetching source code from
`source control server <http://git.savannah.gnu.org/cgit/kenozooid.git>`_, see
:ref:`use-kz-git` subsection.

.. _use-kz-git:

Using Kenozooid From Git
^^^^^^^^^^^^^^^^^^^^^^^^

Python Modules
^^^^^^^^^^^^^^

R Packages
^^^^^^^^^^

.. vim: sw=4:et:ai
