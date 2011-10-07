#
# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2011 by Artur Wroblewski <wrobell@pld-linux.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Kenozooid data flow processing funtions and coroutines.
"""

import itertools
import os
from contextlib import contextmanager
from tempfile import mkstemp

def coroutine(func):
    """
    Decorator for a coroutine function.
    
    Advances a coroutine to its first ``(yield)`` statement.
    """
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        next(cr)
        return cr
    return start


def pipe(data, *gens):
    """
    Pipe data through list of geneators.
    
    :Parameters:
     data
        Data to pipe through the generators.
     gens
        List of generators to process the data.
    """
    for g in gens:
        data = g(data)
    return data


def send(data, tc):
    """
    Send data from iterator to target coroutine.

    :Parameters:
     data
        Iterator of data to send.
     tc
        Coroutine to receive the data.
    """
    for v in data:
        tc.send(v)
    tc.close()


@coroutine
def split(*tc):
    """
    Coroutines to receive a value and send it to all coroutines specified
    in ``tc`` list.

    :Parameters:
     tc
        List of target coroutines.
    """
    while True:
        v = yield
        for c in tc:
            c.send(v)


@coroutine
def concat(n, cat=itertools.chain, tc=None):
    """
    Coroutine to concatenate data from ``n`` sources.

    The coroutines receives ``n`` sources of data and passes them to
    ``cat`` function. The concatenate result is sent to ``tc`` target
    coroutine.

    :Parameters:
     n
        Amount of data sources.
     cat
        Function to concatenate data.
     tc
        Target coroutine.
    """
    values = []
    for i in range(n):
        values.append((yield))
    rv = cat(*values)
    if tc is not None:
        tc.send(rv)


@coroutine
def sink(f):
    """
    A sink coroutine to receive a value and execute with function ``f``.
    """
    while True:
        v = yield
        f(v)


@coroutine
def buffer(f, tc=None):
    """
    Coroutine buffer received data in a file.

    When coroutine is closed, then file object is sent to target coroutine.

    :Parameters:
     f
        File object to store buffered data.
     tc
        Target coroutine.
    """
    try:
        while True:
            lines = yield
            f.writelines(lines)
    except GeneratorExit:
        if tc is not None:
            tc.send(f)


@contextmanager
def buffer_open(n):
    """
    Open ``n`` buffer files.
    """
    files = []
    files.extend(mkstemp() for i in range(n))
    fds = tuple(open(fd, 'w+') for fd, fn in files)
    yield fds
    for (_, fn), fd in zip(files, fds):
        fd.close()
        os.remove(fn)

# vim: sw=4:et:ai
