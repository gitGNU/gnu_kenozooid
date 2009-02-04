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

from docutils import nodes, utils

def api_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    basedir = 'api'

    name = '%s' % text
    file = '%s/%s-module.html' % (basedir, text)

    node = nodes.reference(rawtext, name, refuri=file, **options)
    return [node], []


def setup(app):
    app.add_role('api', api_role)

