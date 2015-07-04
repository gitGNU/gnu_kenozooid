import sys
import os.path

import alabaster

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('doc'))

import kenozooid

extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.autosummary', 'sphinx.ext.doctest',
    'sphinx.ext.todo', 'sphinx.ext.viewcode', 'extapi', 'alabaster'
]

project = 'Kenozooid'
source_suffix = '.rst'
master_doc = 'index'

version = kenozooid.__version__
release = kenozooid.__version__
copyright = 'Kenozooid team'

epub_basename = 'Kenozooid - {}'.format(version)
epub_author = 'Kenozooid team'

html_theme_path = [alabaster.get_path()]
html_static_path = ['static']
html_theme = 'alabaster'
html_style = 'kenozooid.css'

# vim: sw=4:et:ai
