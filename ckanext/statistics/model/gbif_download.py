
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from ckanext.statistics.model import Base
from sqlalchemy import Column, DateTime, Integer, String, func


class GBIFDownload(Base):
    '''Table for holding resource stats'''
    __tablename__ = u'gbif_downloads'

    doi = Column(String, primary_key=True)
    date = Column(DateTime)  # the current timestamp
    inserted_on = Column(DateTime, default=func.now())  # the current timestamp
    count = Column(Integer)
