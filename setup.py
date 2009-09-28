#!/usr/bin/python

from setuptools import setup, find_packages

version = __import__('kenozooid').__version__

from distutils.cmd import Command

class EpydocBuildDoc(Command):
    description = 'Builds the documentation with epydoc'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        epydoc_conf = 'doc/epydoc.conf'

        try:
            import sys
            from epydoc import cli
            old_argv = sys.argv[1:]
            sys.argv[1:] = [
                '--config=%s' % epydoc_conf,
                '--no-private',
                '--simple-term',
                '--verbose'
            ]
            cli.cli()
            sys.argv[1:] = old_argv

        except ImportError:
            print 'epydoc not installed, skipping API documentation'



class build_doc(Command):
    description = 'Builds the documentation'
    user_options = []

    def __init__(self, dist):
        self.epydoc = EpydocBuildDoc(dist)
        self.sphinx = None
        try:
            from sphinx.setup_command import BuildDoc as SphinxBuildDoc
            self.sphinx = SphinxBuildDoc(dist)
        except ImportError:
            print 'sphinx not installed, skipping user documentation'

        Command.__init__(self, dist)


    def initialize_options(self):
        if self.sphinx:
            self.sphinx.initialize_options()
        self.epydoc.initialize_options()


    def finalize_options(self):
        if self.sphinx:
            self.sphinx.finalize_options()
        self.epydoc.finalize_options()


    def run(self):
        if self.sphinx:
            self.sphinx.run()
        self.epydoc.run()


setup(
    name='kenozooid',
    version=version,
    description='Software stack to support different capabilities of dive computers',
    author='Artur Wroblewski',
    author_email='wrobell@pld-linux.org',
    url='http://wrobell.it-zone.org/kenozooid',
    packages=find_packages('.'),
    long_description=\
"""\
Kenozooid is software stack to support different capabilities of dive
computers.
""",
    classifiers=[
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Topic :: Internet',
    ],
    keywords='diving dive computer logger plot dump uddf',
    license='GPL',
    install_requires=[
        'lxml >= 2.2.2',
        'matplotlib >= 0.99.0',
        'nose >= 0.10.4',
        'pyserial >= 2.4',
        'setuptools',
    ],
    entry_points={
        'console_scripts': [
            'kenozooid = bin.kenozooid:__main__',
        ],
    },
    test_suite='nose.collector',
    cmdclass={'build_epydoc': EpydocBuildDoc, 'build_doc': build_doc},
)

