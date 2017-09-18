#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import sys
import os
import ckan.model as model
from ckan.model.resource import Resource
from sqlalchemy import MetaData, Column, Integer, String, DateTime, UnicodeText, ForeignKey, func


from ckanext.statistics.model import Base


class GBIFDownload(Base):
    """
    Table for holding resource stats
    """
    __tablename__ = 'gbif_downloads'

    doi = Column(String, primary_key=True)
    date = Column(DateTime)  # the current timestamp
    inserted_on = Column(DateTime, default=func.now())  # the current timestamp
    count = Column(Integer)
