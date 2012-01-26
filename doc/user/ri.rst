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
| lxml            |   2.3    | Python      | Fedora 15, Mac OS X,     | XML parsing and searching  |
|                 |          | module      | PLD Linux, Windows       |                            |
+-----------------+----------+-------------+--------------------------+----------------------------+
| dirty           |  1.0.2   | Python      | Mac OS X, PLD Linux,     | XML data generation        |
|                 |          | module      | Windows                  |                            |
+-----------------+----------+-------------+--------------------------+----------------------------+
| dateutil        |   2.0    | Python      | Mac OS X, PLD Linux,     | date and time parsing      |
|                 |          | module      | Windows                  |                            |
+-----------------+----------+-------------+--------------------------+----------------------------+
|                                           **Optional**                                           |
+-----------------+----------+-------------+--------------------------+----------------------------+
| pyserial        |    2.6   | Python      | PLD Linux, Windows       | required by OSTC driver    |
|                 |          | module      |                          |                            |
+-----------------+----------+-------------+--------------------------+----------------------------+
| libdivecomputer |          | library     |                          | required by Sensus Ultra   |
|                 |          |             |                          | driver                     |
+-----------------+----------+-------------+--------------------------+----------------------------+
| R               |  2.13.0  | R scripts   | Arch, Debian Wheezy,     | plotting and dive data     |
|                 |          | execution   | Fedora 15, Mac OS X,     | analysis                   |
|                 |          | environment | PLD Linux, Ubuntu Natty, |                            |
|                 |          |             | Windows                  |                            |
+-----------------+----------+-------------+--------------------------+----------------------------+
| rpy             |  2.2.1   | Python      | PLD Linux                | used to communicate with R |
|                 |          | module      |                          |                            |
+-----------------+----------+-------------+--------------------------+----------------------------+
| Hmisc           |          | R package   |                          | used for plotting          |
+-----------------+----------+-------------+--------------------------+----------------------------+
| colorspace      |          | R package   |                          | used for overlay plotting  |
+-----------------+----------+-------------+--------------------------+----------------------------+

Installation
------------

Kenozooid Installation
^^^^^^^^^^^^^^^^^^^^^^
Kenozooid can be downloaded from `PyPI <http://pypi.python.org/pypi>`_

    http://pypi.python.org/pypi/kenozooid

Unpack the downloaded archive and use the following command to install
Kenozooid::

    $ python3 setup.py install

The :ref:`user-kz-deps` section describes how to check additional Kenozooid
dependencies like `R <http://www.r-project.org/>`_ and R packages needed for
plotting and data analysis.

.. _user-kz-git:

At the Bleeging Edge of Kenozooid Development
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Kenozooid can be used directly after fetching source code from its
`Git <http://git-scm.com/>`_ repository. This allows to follow Kenozooid
development and use its unstable but latest features.

Kenozooid source code is hosted on `Savannah <http://savannah.gnu.org/>`_ at

    http://git.savannah.gnu.org/cgit/kenozooid.git

To check out from the repository simply type::

    git clone http://git.savannah.gnu.org/r/kenozooid.git

After fetching the source code enter Kenozooid directory, set up paths and
simply invoke Kenozooid command line interface, for example::

    cd kenozooid
    export PYTHONPATH=.:$PYTHONPATH
    export PATH=./bin:$PATH
    kz --help

.. _user-kz-deps:

Checking Dependencies
^^^^^^^^^^^^^^^^^^^^^
The Kenozooid dependencies can be checked with 'setup.py' script, which is part
of Kenozooid source code. The dependency checking verifies version of Python
used and installation of Python modules and R packages.

To check the dependencies execute the following command from Kenozooid's source
code directory::

    python3 setup.py deps

Example, fully successful output of dependency check, can be as follows::

    $ python3 setup.py deps
    running deps
    Checking Kenozooid dependencies
    Checking Python version >= 3.2... ok
    Checking core Python module lxml... ok
    Checking core Python module dirty >= 1.0.2... ok
    Checking core Python module dateutil... ok
    Checking optional Python module rpy2... ok
    Checking optional Python module serial... ok
    Checking R package Hmisc... ok
    Checking R package colorspace... ok

Example, successful output of dependency check, but with missing optional
dependencies, might look in the following way::

    $ python3 setup.py deps
    running deps
    Checking Kenozooid dependencies
    Checking Python version >= 3.2... ok
    Checking core Python module lxml... ok
    Checking core Python module dirty >= 1.0.2... ok
    Checking core Python module dateutil... ok
    Checking optional Python module rpy2... ok
    Checking optional Python module serial... not found
    Checking R package Hmisc... not found
    Checking R package colorspace... ok

    Missing optional dependencies:

      Install serial Python module with command

          easy_install-3.2 --user pyserial

      Install Hmisc R package by starting R and invoking command

          install.packages('Hmisc')

R Packages Tips
^^^^^^^^^^^^^^^
R is very sophisticated and powerful statistical software with many addons
distributed via `The Comprehensive R Archive Network <http://cran.r-project.org/>`_.

When installing R packages required by Kenozooid, some additional software
might be needed

- Fortran compiler is required to compile some R packages, i.e. ``Hmisc``;
  on Linux gcc-fortran package should be installed

.. vim: sw=4:et:ai
