import sys
import os.path

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('doc'))

import kenozooid

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.todo',
    'extapi']
project = 'Kenozooid'
source_suffix = '.txt'
master_doc = 'index'

version = kenozooid.__version__
release = kenozooid.__version__
