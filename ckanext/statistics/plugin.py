from logging import getLogger
import ckan.plugins as p
from ckanext.statistics.logic.action import download_statistics, dataset_statistics


class StatisticsPlugin(p.SingletonPlugin):
    """
    NHM Statistics
    """

    p.implements(p.IActions)

    # IActions
    @staticmethod
    def get_actions():
        return {
            'download_statistics': download_statistics,
            'dataset_statistics': dataset_statistics
        }
