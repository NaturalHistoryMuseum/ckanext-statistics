# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from ckan.model import meta, DomainObject
from sqlalchemy import Column, DateTime, Integer, func, Table

gbif_downloads_table = Table(
    u'gbif_downloads',
    meta.metadata,
    Column(u'doi', Integer, primary_key=True),
    Column(u'date', DateTime),
    # the current timestamp
    Column(u'inserted_on', DateTime, default=func.now()),
    Column(u'count', Integer),
)


class GBIFDownload(DomainObject):
    '''
    Object for a datastore download row.
    '''
    pass


meta.mapper(GBIFDownload, gbif_downloads_table)
