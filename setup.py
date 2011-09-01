#!/usr/bin/env python3

from setuptools import setup, find_packages
from collections import OrderedDict
import sys

version = __import__('kenozooid').__version__

from distutils.cmd import Command
import os.path


def _py_inst(mods, names, py_miss):
    """
    Print Python module installation suggestion.
    """
    for i, (m, n) in enumerate(zip(mods, names)):
        if m not in py_miss:
            continue

        print('''\
  Install {} Python module with command

      easy_install-3.2 --user {}
'''.format(m, n))

class CheckDeps(Command):
    description = 'Check core and optional Kenozooid dependencies'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        python_ok = sys.version_info >= (3, 2)
        rpy_ok = False
        mods = 'lxml', 'dateutil', 'rpy2', 'serial'
        names = 'lxml', 'python-dateutil', 'rpy2', 'pyserial'
        ic = 2
        py_miss = set()
        r_miss = set()

        print('Checking Kenozooid dependencies')

        print('Checking Python version >= 3.2... {}' \
                .format('ok' if python_ok else 'no'))

        # check Python modules
        for i, m in enumerate(mods):
            try:
                t = 'core' if i < ic else 'optional'
                print('Checking {} Python module {}... '.format(t, m), end='')
                __import__(m)
                print('ok')
            except ImportError:
                print('not found')
                py_miss.add(m)

        # check R packages
        rpy_ok = 'rpy2' not in py_miss 
        if rpy_ok:
            import rpy2
            from rpy2.robjects.packages import importr
            try:
                print('Checking R package Hmisc... ', end='')
                importr('Hmisc')
                print('ok')
            except rpy2.rinterface.RRuntimeError:
                print('not found')
                r_miss.add('Hmisc')
        else:
            print('No rpy2 installed, not checking R packages installation')

        # print installation suggestions
        if py_miss and py_miss.intersection(mods[:ic]) or not python_ok :
            print('\nMissing core dependencies:\n')
        if not python_ok:
            print('  Use Python 3.2 at least!!!\n')
        _py_inst(mods[:ic], names, py_miss)

        if py_miss and py_miss.intersection(mods[ic:]):
            print('\nMissing optional dependencies:\n')
        _py_inst(mods[ic:], names, py_miss)

        for p in r_miss:
            print('''\
  Install {p} R package by starting R and invoking command

      install.packages('{p}')
'''.format(p=p))



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
            print('epydoc not installed, skipping API documentation')



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
            print('sphinx not installed, skipping user documentation')

        Command.__init__(self, dist)


    def initialize_options(self):
        if self.sphinx:
            self.sphinx.initialize_options()
        self.epydoc.initialize_options()


    def finalize_options(self):
        build = self.get_finalized_command('build')
        d1 = os.path.join(build.build_base, 'homepage', 'doc', 'api')
        self.mkpath(d1)

        if self.sphinx:
            self.sphinx.build_dir = os.path.join(build.build_base,
                'homepage', 'doc')
            self.sphinx.finalize_options()
        self.epydoc.finalize_options()


    def run(self):
        self.epydoc.run()
        if self.sphinx:
            self.sphinx.run()
        # fixme
        os.system('cp -r doc/homepage build')


setup(
    name='kenozooid',
    version=version,
    description='Kenozooid is dive planning and analysis toolbox',
    author='Artur Wroblewski',
    author_email='wrobell@pld-linux.org',
    url='http://wrobell.it-zone.org/kenozooid',
    packages=find_packages('.'),
    long_description=\
"""\
Kenozooid is dive planning and analysis toolbox.
""",
    classifiers=[
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    keywords='diving dive computer logger plot dump uddf analytics',
    license='GPL',
    install_requires=[
        'lxml >= 2.3',
        'python-dateutil >= 2.0',
        #'pyserial >= 2.5',
        #'rpy2 >= 2.2.2',
        'distribute',
        'setuptools-git',
    ],
    test_suite='nose.collector',
    cmdclass={
        'build_epydoc': EpydocBuildDoc,
        'build_doc': build_doc,
        'deps': CheckDeps,
    },
    include_package_data=True,
)

# vim: sw=4:et:ai
