
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from setuptools import find_packages, setup

__version__ = u'0.2'

setup(
    name=u'ckanext-statistics',
    version=__version__,
    description=u'NHM Stats plugin.',
    long_description=u'',
    classifiers=[],
    keywords=u'',
    author=u'Natural History Museum',
    author_email=u'data@nhm.ac.uk',
    url=u'',
    license=u'',
    packages=find_packages(exclude=[u'ez_setup', u'stats', u'tests']),
    namespace_packages=[u'ckanext', u'ckanext.statistics'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points= \
        u'''
            [ckan.plugins]
            statistics=ckanext.statistics.plugin:StatisticsPlugin
            [paste.paster_command]
            statistics=ckanext.statistics.commands.statistics:StatisticsCommand
        ''',
    )
