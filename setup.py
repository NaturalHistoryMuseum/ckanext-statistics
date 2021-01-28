#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = u'1.0.1'

with open(u'README.md', u'r') as f:
    __long_description__ = f.read()


def nhm_github(name, tag):
    return name, u'git+https://github.com/NaturalHistoryMuseum/{name}.git@{tag}#egg={name}'.format(
        name=name, tag=tag)


dependencies = dict([
    nhm_github(u'ckanext-ckanpackager', u'319bd63158757a9287336034122cae66c2991a41'),
    nhm_github(u'ckanext-versioned-datastore', u'd88e167a838e95af2448b60c7df67f2e2fe86eed'),
])

setup(
    name=u'ckanext-statistics',
    version=__version__,
    description=u'A CKAN extension for accessing instance statistics.',
    long_description=__long_description__,
    classifiers=[
        u'Development Status :: 3 - Alpha',
        u'Framework :: Flask',
        u'Programming Language :: Python :: 2.7'
    ],
    keywords=u'CKAN data statistics',
    author=u'Natural History Museum',
    author_email=u'data@nhm.ac.uk',
    url=u'https://github.com/NaturalHistoryMuseum/ckanext-statistics',
    license=u'GNU GPLv3',
    packages=find_packages(exclude=[u'tests']),
    namespace_packages=[u'ckanext', u'ckanext.statistics'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        u'requests',
        u'tqdm>=4.55.1',
    ] + [u'{0} @ {1}'.format(k, v) for k, v in dependencies.items()],
    dependency_links=list(dependencies.values()),
    entry_points=u'''
        [ckan.plugins]
            statistics=ckanext.statistics.plugin:StatisticsPlugin
        ''',
    )
