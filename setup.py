#!/usr/bin/env python
#This file is not yet part of Tryton.
#This repository contains the full copyright notices and license terms.

from setuptools import setup
import re
import os
import ConfigParser


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

config = ConfigParser.ConfigParser()
config.readfp(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
major_version, minor_version, _ = info.get('version', '0.0.1').split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

requires = []
for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        requires.append('trytond_%s >= %s.%s' %
                (dep, major_version, minor_version,))
requires.append('trytond >= %s.%s' %
        (major_version, minor_version,))

setup(name='trytond_accounting_uk_chart',
    version=info.get('version', '0.0.1'),
    description='Tryton module for UK chart of accounts',
    long_description=read('README.md'),
    author='Lampman Tech',
    url='https://github.com/lampmantech/trytond_accounting_uk_chart',
    download_url=("git://github.com/lampmantech/trytond_accounting_uk_chart.git"),
    package_dir={'trytond.modules.accounting_uk_chart': '.'},
    packages=[
        'trytond.modules.accounting_uk_chart',
        ],
    package_data={
        'trytond.modules.accounting_uk_chart': (info.get('xml', [])
            + ['tryton.cfg']),
        },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Plugins',
        'Framework :: Tryton',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial :: Accounting',
        ],
    license='GPL-3',
    install_requires=requires,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    accounting_uk_chart = trytond.modules.accounting_uk_chart
    """,
    )
