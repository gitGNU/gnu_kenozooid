#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name='kenozooid',
    version='0.1',
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
    keywords='diving plot dump uddf',
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

)
