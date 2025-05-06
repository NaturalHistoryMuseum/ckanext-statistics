# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK

from ckan.model import DomainObject, meta
from sqlalchemy import Column, DateTime, Integer, Table, UnicodeText, func

"""
This table has been copied from the now deprecated ckanext-ckanpackager extension to
enable ongoing compatibility without having to depend on that extension.
"""


ckanpackager_stats_table = Table(
    'ckanpackager_stats',
    meta.metadata,
    Column('id', Integer, primary_key=True),
    # the current timestamp
    Column('inserted_on', DateTime, default=func.now()),
    Column('count', Integer),
    Column('resource_id', UnicodeText),
)


class CKANPackagerStat(DomainObject):
    """
    Object for a datastore download row.
    """

    pass


meta.mapper(CKANPackagerStat, ckanpackager_stats_table)
