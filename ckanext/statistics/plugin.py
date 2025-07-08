# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from beaker.cache import cache_regions
from ckan.plugins import SingletonPlugin, implements, interfaces

from ckanext.statistics.logic.action import dataset_statistics, download_statistics


class StatisticsPlugin(SingletonPlugin):
    """
    NHM Statistics.
    """

    implements(interfaces.IActions)
    implements(interfaces.IConfigurable)

    # IActions
    @staticmethod
    def get_actions():
        return {
            'download_statistics': download_statistics,
            'dataset_statistics': dataset_statistics,
        }

    # IConfigurable
    def configure(self, config):
        # configure cache
        options = {}
        for k, v in config.items():
            if k.startswith('ckanext.statistics.cache.'):
                options[k.split('.')[-1]] = v
        cache_regions.update({'ckanext_statistics': options})
