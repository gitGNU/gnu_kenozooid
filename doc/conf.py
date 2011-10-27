import sys
import os.path

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('doc'))

import kenozooid

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.todo',
    'sphinx.ext.viewcode', 'extapi']
project = 'Kenozooid'
source_suffix = '.rst'
master_doc = 'index'

version = kenozooid.__version__
release = kenozooid.__version__
copyright = 'Kenozooid team'

epub_basename = 'Kenozooid - {}'.format(version)
epub_author = 'Kenozooid team'


# see https://bitbucket.org/birkenfeld/sphinx/issue/635/no-attribute-next
import sphinx.jinja2glue
if not hasattr(sphinx.jinja2glue.idgen, "next"):
      sphinx.jinja2glue.idgen.next = sphinx.jinja2glue.idgen.__next__

# vim: sw=4:et:ai
