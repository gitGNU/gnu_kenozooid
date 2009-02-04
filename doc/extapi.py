#
# Kenozooid - software stack to support different capabilities of dive
# computers.
#
# Copyright (C) 2009 by Artur Wroblewski <wrobell@pld-linux.org>
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

import os.path
from docutils import nodes

def api_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    basedir = 'api'
    prefix = 'doc/_build/html/' # fixme: fetch it from configuration
    exists = lambda f: os.path.exists(prefix + f)

    name = '%s' % text
    file = '%s/%s-module.html' % (basedir, text)
    if not exists(file):
        name = text.split('.')[-1]
        file = '%s/%s-class.html' % (basedir, text)
    if not exists(file):
        chunks = text.split('.')
        method = chunks[-1]
        file = '%s/%s-module.html' % (basedir, '.'.join(chunks[:-1]))
        if exists(file):
            file = '%s#%s' % (file, method)
        else:
            file = '%s/%s-class.html' % (basedir, '.'.join(chunks[:-1]))
            if exists(file):
                file = '%s/%s-class.html#%s' % (basedir, '.'.join(chunks[:-1]), method)
            #else:
            #    # cannot find reference, just inline the text
            #    return [nodes.literal(rawtext, text)], []

    node = nodes.reference(rawtext, name, refuri=file, **options)
    return [node], []


def setup(app):
    app.add_role('api', api_role)

