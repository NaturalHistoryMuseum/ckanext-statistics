import copy
import json
import os
from sqlalchemy import sql, case
from collections import OrderedDict
import ckan.plugins as p
from ckan.plugins import PluginImplementations
from ckan.lib.navl.dictization_functions import validate
import ckanext.datastore.helpers as datastore_helpers

from pylons import config
import ckan.model as model
from ckan.model.resource import Resource, ResourceGroup
from ckan.model.package import Package
from ckanext.statistics.model.gbif_download import GBIFDownload
from ckanext.ckanpackager.model.stat import CKANPackagerStat

from ckanext.statistics.lib.statistics import Statistics
from ckanext.statistics.logic.schema import statistics_downloads_schema


class DownloadStatistics(Statistics):
    """
    Class used to implement the download statistics action
    Show records downloaded etc.,
    """

    schema = statistics_downloads_schema()

    def _get_statistics(self, year=None, month=None):
        """
        Fetch the statistics
        """
        result = self.ckanpackager_stats(year, month)
        backfill = self._backfill_stats(year, month)
        stats = self._merge(result, backfill)
        # Merge in the GBIF stats
        for k, v in self.gbif_stats(year, month).items():
            result.setdefault(k, default={})
            result[k]['gbif'] = v
        return result

    @staticmethod
    def gbif_stats(year=None, month=None):
        """
        Get GBIF download stats
        @param year:
        @param month:
        @return: dict
        """

        stats = OrderedDict()

        year_part = sql.func.date_part('year', GBIFDownload.date).label('year')
        month_part = sql.func.date_part('month', GBIFDownload.date).label('month')

        rows = model.Session.query(
            sql.func.concat(month_part, '/', year_part).label("date"),
            sql.func.sum(GBIFDownload.count).label("records"),
            sql.func.count().label("download_events")
        ).group_by(
            year_part,
            month_part
        )
        if year:
            rows = rows.filter(sql.extract('year', GBIFDownload.date) == year)
        if month:
            rows = rows.filter(sql.extract('month', GBIFDownload.date) == month)

        rows = rows.order_by(month_part, year_part).all()

        for row in rows:
            stats[row.__dict__['date']] = {
                'records': int(row.__dict__['records']),
                'download_events': int(row.__dict__['download_events'])
            }

        return stats

    @staticmethod
    def ckanpackager_stats(year=None, month=None):
        """
        Get ckan packager stats
        @param year:
        @param month:
        @return:
        """

        stats = OrderedDict()
        indexlot_resource_id = config.get("ckanext.nhm.indexlot_resource_id")
        specimen_resource_id = config.get("ckanext.nhm.specimen_resource_id")

        year_part = sql.func.date_part('year', CKANPackagerStat.inserted_on).label('year')
        month_part = sql.func.date_part('month', CKANPackagerStat.inserted_on).label('month')
        rows = model.Session.query(
            sql.func.concat(month_part, '/', year_part).label("date"),
            sql.func.sum(CKANPackagerStat.count).label("records"),
            sql.func.count('id').label("download_events"),
            case(
                {
                    specimen_resource_id: True,
                    indexlot_resource_id: True
                },
                value=CKANPackagerStat.resource_id,
                else_=False
            ).label("collection")

        ).group_by(
            year_part,
            month_part,
            "collection"
        )
        if year:
            rows = rows.filter(sql.extract('year', CKANPackagerStat.inserted_on) == year)
        if month:
            rows = rows.filter(sql.extract('month', CKANPackagerStat.inserted_on) == month)

        rows = rows.order_by(month_part, year_part).all()

        for row in rows:
            stats.setdefault(row.__dict__['date'], default={})
            key = 'collections' if row.__dict__['collection'] else 'research'
            stats[row.__dict__['date']][key] = {
                'records': int(row.__dict__['records']),
                'download_events': int(row.__dict__['download_events'])
            }
        return stats

    @staticmethod
    def _backfill_stats(year=None, month=None):
        '''
        Loads static data from a json file that can be used to fill gaps in the API's returned statistics.
        :param year: the year to load data for
        :type year:
        :param month: the month to load data for
        :type month:
        :return: a dictionary of download statistics keyed on month/year
        :rtype:
        '''
        backfill_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/data-portal-backfill.json')
        with open(backfill_file, 'r') as jsonfile:
            backfill_data = json.load(jsonfile)

        if year:
            backfill_data = {k: v for k, v in backfill_data.items() if k == str(year)}
        if month:
            backfill_data = {y: {m: w for m, w in v.items() if m == str(month)} for y, v in backfill_data.items()}

        stats = {}
        for y in backfill_data:
            for m in backfill_data[y]:
                stats['{0}/{1}'.format(m, y)] = backfill_data[y][m]

        return stats

    @staticmethod
    def _merge(stats_1, stats_2):
        all_keys = list(set(stats_1.keys + stats_2.keys))
        stats_3 = {k: {} for k in all_keys}
        for key in all_keys:
            key_stats = {}
            sub_keys = list(set(stats_1.get(key, {}).keys + stats_2.get(key, {}).keys))
            for sub in sub_keys:
                key_stats[sub] = {}