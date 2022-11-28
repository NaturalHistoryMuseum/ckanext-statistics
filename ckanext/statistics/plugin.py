# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from ckan.plugins import SingletonPlugin, implements, interfaces

from ckanext.statistics.logic.action import dataset_statistics, download_statistics
from . import cli


class StatisticsPlugin(SingletonPlugin):
    """
    NHM Statistics.
    """

    implements(interfaces.IActions)
    implements(interfaces.IClick)

    # IActions
    @staticmethod
    def get_actions():
        return {
            'download_statistics': download_statistics,
            'dataset_statistics': dataset_statistics,
        }

    # IClick
    def get_commands(self):
        return cli.get_commands()
