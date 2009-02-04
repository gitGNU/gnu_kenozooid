import sys
import os.path

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('doc'))

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.todo',
    'extapi']
project = 'Kenozooid'
source_suffix = '.txt'
master_doc = 'contents'

