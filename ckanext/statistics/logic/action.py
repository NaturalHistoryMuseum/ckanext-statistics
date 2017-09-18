import ckan.logic as logic

from ckanext.statistics.lib.download_statistics import DownloadStatistics
from ckanext.statistics.lib.dataset_statistics import DatasetStatistics

@logic.side_effect_free
def download_statistics(context, data_dict):
    """
    Data Portal Download stats
    @param context:
    @param data_dict:
    @return:
    """
    statistics = DownloadStatistics(context, data_dict)
    statistics.validate()
    return statistics.get()


@logic.side_effect_free
def dataset_statistics(context, data_dict):
    """
    Data Portal Download stats
    @param context:
    @param data_dict:
    @return:
    """
    statistics = DatasetStatistics(context, data_dict)
    statistics.validate()
    return statistics.get()
