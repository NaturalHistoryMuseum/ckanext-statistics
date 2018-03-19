
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


import json
from collections import OrderedDict
from datetime import datetime as dt

import os
from ckanext.ckanpackager.model.stat import CKANPackagerStat
from ckanext.statistics.lib.statistics import Statistics
from ckanext.statistics.logic.schema import statistics_downloads_schema
from ckanext.statistics.model.gbif_download import GBIFDownload
from sqlalchemy import case, sql

import ckan.model as model
from ckan.plugins import toolkit


class DownloadStatistics(Statistics):
    '''Class used to implement the download statistics action.
    Show records downloaded etc.

    '''

    schema = statistics_downloads_schema()

    def _get_statistics(self, year=None, month=None):
        '''Fetch the statistics

        :param year: (optional, default: None)
        :param month: (optional, default: None)
        :returns: dict of stats

        '''
        stats = self.ckanpackager_stats(year, month)
        backfill = self.backfill_stats(u'data-portal-backfill.json', year, month)
        result = self.merge(stats, backfill)
        # Merge in the GBIF stats
        for k, v in self.gbif_stats(year, month).items():
            result.setdefault(k, default={})
            result[k][u'gbif'] = v
        return result

    @staticmethod
    def gbif_stats(year=None, month=None):
        '''Get GBIF download stats

        :param year: (optional, default: None)
        :param month: (optional, default: None)
        :returns: dict of GBIF stats

        '''

        stats = OrderedDict()

        year_part = sql.func.date_part(u'year', GBIFDownload.date).label(u'year')
        month_part = sql.func.date_part(u'month', GBIFDownload.date).label(
            u'month')

        rows = model.Session.query(
            sql.func.concat(month_part, '/', year_part).label(u'date'),
            sql.func.sum(GBIFDownload.count).label(u'records'),
            sql.func.count().label(u'download_events')
            ).group_by(
            year_part,
            month_part
            )
        if year:
            rows = rows.filter(sql.extract(u'year', GBIFDownload.date) == year)
        if month:
            rows = rows.filter(
                sql.extract(u'month', GBIFDownload.date) == month)

        rows = rows.order_by(month_part, year_part).all()

        for row in rows:
            stats[row.__dict__[u'date']] = {
                u'records': int(row.__dict__[u'records']),
                u'download_events': int(row.__dict__[u'download_events'])
                }

        return stats

    @staticmethod
    def ckanpackager_stats(year=None, month=None):
        '''Get ckan packager stats

        :param year: (optional, default: None)
        :param month: (optional, default: None)
        :returns: dict of ckanpackager stats

        '''

        stats = OrderedDict()
        indexlot_resource_id = toolkit.config.get(u'ckanext.nhm.indexlot_resource_id')
        specimen_resource_id = toolkit.config.get(u'ckanext.nhm.specimen_resource_id')

        year_part = sql.func.date_part(u'year',
                                       CKANPackagerStat.inserted_on).label(
            u'year')
        month_part = sql.func.date_part(u'month',
                                        CKANPackagerStat.inserted_on).label(
            u'month')
        rows = model.Session.query(
            sql.func.concat(month_part, '/', year_part).label(u'date'),
            sql.func.sum(CKANPackagerStat.count).label(u'records'),
            sql.func.count(u'id').label(u'download_events'),
            case(
                {
                    specimen_resource_id: True,
                    indexlot_resource_id: True
                    },
                value=CKANPackagerStat.resource_id,
                else_=False
                ).label(u'collection')

            ).group_by(
            year_part,
            month_part,
            u'collection'
            )
        if year:
            rows = rows.filter(
                sql.extract(u'year', CKANPackagerStat.inserted_on) == year)
        if month:
            rows = rows.filter(
                sql.extract(u'month', CKANPackagerStat.inserted_on) == month)

        rows = rows.order_by(month_part, year_part).all()

        for row in rows:
            stats.setdefault(row.__dict__[u'date'], default={})
            key = u'collections' if row.__dict__[u'collection'] else u'research'
            stats[row.__dict__[u'date']][key] = {
                u'records': int(row.__dict__[u'records']),
                u'download_events': int(row.__dict__[u'download_events'])
                }
        return stats

    @staticmethod
    def backfill_stats(filename, year=None, month=None):
        '''Loads static data from a json file that can be used to fill gaps in
        the API's returned statistics.

        :param filename: the name of the json file containing the statistics
        :param year: the year to load data for (optional, default: None)
        :param month: the month to load data for (optional, default: None)
        :returns: a dictionary of download statistics keyed on month/year

        '''
        if filename is None:
            return {}
        backfill_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            u'data', filename)
        with open(backfill_file, u'r') as jsonfile:
            backfill_data = json.load(jsonfile)

        if year:
            backfill_data = {k: v for k, v in backfill_data.items() if
                             k == str(year)}
        if month:
            backfill_data = {y: {m: w for m, w in v.items() if m == str(month)}
                             for y, v in backfill_data.items()}

        stats = {}
        for y in backfill_data:
            for m in backfill_data[y]:
                stats[u'{0}/{1}'.format(m, y)] = backfill_data[y][m]

        return stats

    @staticmethod
    def merge(stats_1, stats_2):
        '''Fills gaps in stats_1 with data from stats_2.

        :param stats_1: the primary dataset (has priority)
        :param stats_2: the secondary dataset to merge into the first
        :returns: an ordered dictionary sorted by month/year

        '''
        all_keys = list(set(stats_1.keys() + stats_2.keys()))
        categories = list(set(
            [i for k in stats_1.values() + stats_2.values() for i in
             k.keys()]))
        stat_names = list(set([i for k in (stats_1.values() +
                                           stats_2.values()) for i in
                               [x for v in k.values() for x in v.keys()]]))
        ordered_stats = OrderedDict()
        for key in sorted(all_keys, key=lambda x: dt.strptime(
                x if len(x) == 7 else u'0' + x, u'%m/%Y')):
            ordered_stats[key] = {
                c: {s: stats_1.get(key, stats_2.get(key)).get(c, {}).get(s, 0) for
                    s in stat_names} for c in categories}
        return ordered_stats
