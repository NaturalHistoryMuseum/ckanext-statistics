from logging import getLogger
import ckan.plugins as p
from ckanext.statistics.logic.action import download_statistics, dataset_statistics

from ckanext.statistics.logic.auth import view_statistics


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
            'download_statistics': download_statistics,
            'dataset_statistics': dataset_statistics
        }

    # IAuthFunctions
    @staticmethod
    def get_auth_functions():
        return {
            'view_statistics': view_statistics
        }
