#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK

import ckan.logic as logic
import ckan.plugins as p

from ckanext.statistics.lib.download_statistics import DownloadStatistics
from ckanext.statistics.lib.dataset_statistics import DatasetStatistics


@logic.side_effect_free
@p.toolkit.auth_allow_anonymous_access
def download_statistics(context, data_dict):
    '''
    Data Portal Download stats
    @param context:
    @param data_dict:
    @return:
    '''
    statistics = DownloadStatistics(context, data_dict)
    statistics.validate()
    return statistics.get()


@logic.side_effect_free
@p.toolkit.auth_allow_anonymous_access
def dataset_statistics(context, data_dict):
    '''
    Data Portal Download stats
    @param context:
    @param data_dict:
    @return:
    '''
    statistics = DatasetStatistics(context, data_dict)
    statistics.validate()
    return statistics.get()
