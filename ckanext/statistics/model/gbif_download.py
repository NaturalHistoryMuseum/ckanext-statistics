# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from ckan.model import meta, DomainObject
from sqlalchemy import Column, DateTime, Integer, func, Table, UnicodeText

gbif_downloads_table = Table(
    'gbif_downloads',
    meta.metadata,
    Column('doi', UnicodeText, primary_key=True),
    Column('date', DateTime),
    # the current timestamp
    Column('inserted_on', DateTime, default=func.now()),
    Column('count', Integer),
)


class GBIFDownload(DomainObject):
    """
    Object for a datastore download row.
    """

    pass


meta.mapper(GBIFDownload, gbif_downloads_table)
