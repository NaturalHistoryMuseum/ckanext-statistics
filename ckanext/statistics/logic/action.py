# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from ckantools.decorators import action

from ckanext.statistics.lib.dataset_statistics import DatasetStatistics
from ckanext.statistics.lib.download_statistics import DownloadStatistics
from ckanext.statistics.logic import schema

download_stats_helptext = 'Record download statistics.'
dataset_stats_helptext = 'Dataset statistics.'


@action(schema.statistics_downloads_schema(), download_stats_helptext, get=True)
def download_statistics(context, year=None, month=None, resource_id=None):
    """
    Data Portal download stats.
    """
    statistics = DownloadStatistics(context)
    return statistics.get(year=year, month=month, resource_id=resource_id)


@action(schema.statistics_dataset_schema(), dataset_stats_helptext, get=True)
def dataset_statistics(context, resource_id=None):
    """
    Data Portal dataset stats.
    """
    statistics = DatasetStatistics(context)
    return statistics.get(resource_id=resource_id)
