#!/usr/bin/env python
# encoding: utf-8
"""
Created by Ben Scott on '24/08/2017'.
"""

from pylons import config
import ckan.model as model
from ckanext.statistics.model.gbif_download import GBIFDownload
from ckanext.ckanpackager.model.stat import CKANPackagerStat
from sqlalchemy import sql, case
from collections import OrderedDict



