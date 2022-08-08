#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = '2.0.11'

with open('README.md', 'r') as f:
    __long_description__ = f.read()


def nhm_github(name, tag):
    return name, f'git+https://github.com/NaturalHistoryMuseum/{name}@{tag}#egg={name}'

dependencies = dict([
    nhm_github('ckanext-ckanpackager', 'v2.1.2'),
    nhm_github('ckanext-versioned-datastore', 'v3.5.1'),
])

setup(
    name='ckanext-statistics',
    version=__version__,
    description='A CKAN extension for accessing instance statistics.',
    long_description=__long_description__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='CKAN data statistics',
    author='Natural History Museum',
    author_email='data@nhm.ac.uk',
    url='https://github.com/NaturalHistoryMuseum/ckanext-statistics',
    license='GNU GPLv3',
    packages=find_packages(exclude=['tests']),
    namespace_packages=['ckanext', 'ckanext.statistics'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests',
        'tqdm>=4.55.1',
    ] + ['{0} @ {1}'.format(k, v) for k, v in dependencies.items()],
    dependency_links=list(dependencies.values()),
    entry_points='''
        [ckan.plugins]
            statistics=ckanext.statistics.plugin:StatisticsPlugin
        ''',
    )
