
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from ckanext.statistics.logic.action import dataset_statistics, download_statistics

from ckan.plugins import SingletonPlugin, implements, interfaces


class StatisticsPlugin(SingletonPlugin):
    '''NHM Statistics'''

    implements(interfaces.IActions)

    # IActions
    @staticmethod
    def get_actions():
        ''' '''
        return {
            u'download_statistics': download_statistics,
            u'dataset_statistics': dataset_statistics
            }
