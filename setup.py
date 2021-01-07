#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = u'1.0.0-alpha'

with open(u'README.md', u'r') as f:
    __long_description__ = f.read()

dependencies = {
    u'ckanext-ckanpackager': u'git+https://github.com/NaturalHistoryMuseum/ckanext-ckanpackager.git#egg=ckanext-ckanpackager',
    u'ckanext-versioned-datastore': u'git+https://github.com/NaturalHistoryMuseum/ckanext-versioned-datastore.git#egg=ckanext-versioned-datastore',
}

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
        'requests',
        'pysolr==3.6.0',
        'tqdm>=4.55.1',
        ] + [u'{0} @ {1}'.format(k, v) for k, v in dependencies.items()],
    dependency_links=dependencies.values(),
    entry_points= \
        u'''
        [ckan.plugins]
            statistics=ckanext.statistics.plugin:StatisticsPlugin

        [paste.paster_command]
            statistics=ckanext.statistics.commands.statistics:StatisticsCommand
        ''',
    )
