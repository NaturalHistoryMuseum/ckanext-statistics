from logging import getLogger
import ckan.plugins as p
from ckanext.statistics.logic.action import download_statistics, dataset_statistics

from ckanext.statistics.logic.auth import view_stats


class StatisticsPlugin(p.SingletonPlugin):
    """
    NHM Statistics
    """

    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)

    # IActions
    @staticmethod
    def get_actions():
        return {
            'download_stats': download_statistics,
            'dataset_stats': dataset_statistics
        }

    # IAuthFunctions
    @staticmethod
    def get_auth_functions():
        return {
            'view_stats': view_stats
        }
