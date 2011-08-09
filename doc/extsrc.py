# base on pyspecific.py from Python 3.2.1
SOURCE_URI = 'http://git.savannah.gnu.org/cgit/kenozooid.git/tree/{}'

from docutils import nodes, utils
from sphinx.util.nodes import split_explicit_title

def source_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    has_t, title, target = split_explicit_title(text)
    title = utils.unescape(title)
    target = utils.unescape(target)
    refnode = nodes.reference(title, title, refuri=SOURCE_URI.format(target))
    return [refnode], []


def setup(app):
    app.add_role('source', source_role)

# vim: sw=4:et:ai
