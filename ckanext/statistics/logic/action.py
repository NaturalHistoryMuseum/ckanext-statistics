# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from ckan.plugins import toolkit

from ckanext.statistics.lib.dataset_statistics import DatasetStatistics
from ckanext.statistics.lib.download_statistics import DownloadStatistics


@toolkit.side_effect_free
@toolkit.auth_allow_anonymous_access
def download_statistics(context, data_dict):
    """
    Data Portal download stats.

    :param context:
    :param data_dict:
    """
    statistics = DownloadStatistics(context, data_dict)
    statistics.validate()
    return statistics.get()


@toolkit.side_effect_free
@toolkit.auth_allow_anonymous_access
def dataset_statistics(context, data_dict):
    """
    Data Portal dataset stats.

    :param context:
    :param data_dict:
    """
    statistics = DatasetStatistics(context, data_dict)
    statistics.validate()
    return statistics.get()
