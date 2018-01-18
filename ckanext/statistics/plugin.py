#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK

from logging import getLogger
import ckan.plugins as p
from ckanext.statistics.logic.action import download_statistics, dataset_statistics


class StatisticsPlugin(p.SingletonPlugin):
    '''
    NHM Statistics
    '''

    p.implements(p.IActions)

    # IActions
    @staticmethod
    def get_actions():
        return {
            u'download_statistics': download_statistics,
            u'dataset_statistics': dataset_statistics
        }
