# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


import json
from collections import OrderedDict
from datetime import datetime as dt

import ckan.model as model
import os
from ckan.plugins import toolkit
from ckanext.ckanpackager.model.stat import CKANPackagerStat
from ckanext.statistics.lib.statistics import Statistics
from ckanext.statistics.logic.schema import statistics_downloads_schema
from ckanext.statistics.model.gbif_download import GBIFDownload
from ckanext.versioned_datastore.model.downloads import DatastoreDownload, state_complete
from sqlalchemy import sql


class MonthlyStats(object):
    '''
    Class used to keep track of the monthly download counts from multiple sources.
    '''

    def __init__(self, month=None, year=None, resource_id=None):
        '''
        :param month: if passed, only this month will be counted (defaults to None)
        :param year: if passed, only this year will be counted (defaults to None)
        :param resource_id: if passed, only this resource will be counted (defaults to None)
        '''
        self.month = int(month) if month is not None else None
        self.year = int(year) if year is not None else None
        self.resource_id = resource_id

        self.stats = {}
        # extract the collection resource ids from the config
        self.resource_ids = toolkit.config.get(u'ckanext.statistics.resource_ids', set())
        if self.resource_ids:
            self.resource_ids = set(self.resource_ids.split(u' '))

    def add(self, date, resource_id, count):
        '''
        Updates the stats with the download event information for the given resource and count at
        the given date.

        :param date: the date of the download event
        :param resource_id: the resource downloaded
        :param count: the number of records downloaded
        '''
        self.add_all(date, {resource_id: count})

    def add_all(self, date, resource_counts):
        '''
        Updates the stats with the download event information for the given resources and counts at
        the given date. This function filters out information about months/years/resources we're
        not interested in based on the parameters passed during the construction of this object.

        :param date: the date of the download event
        :param resource_counts: a dict of resource ids -> counts
        '''
        month_year = date.strftime(u'%-m/%Y')
        month, year = map(int, month_year.split(u'/'))

        # filter the download event
        if self.resource_id is not None:
            if self.resource_id in resource_counts:
                # only update with counts for the resource id requested
                resource_counts = {self.resource_id: resource_counts[self.resource_id]}
            else:
                return
        if self.month is not None and self.month != month:
            return
        if self.year is not None and self.year != year:
            return

        for resource_id, count in resource_counts.items():
            # if the month/year combo hasn't been seen yet, default it
            if month_year not in self.stats:
                self.stats[month_year] = {
                    u'collections': {
                        u'records': 0,
                        u'download_events': 0
                    },
                    u'research': {
                        u'records': 0,
                        u'download_events': 0
                    }
                }
            resource_type = u'collections' if resource_id in self.resource_ids else u'research'
            self.stats[month_year][resource_type][u'records'] += count

        resources = set(resource_counts.keys())
        if self.resource_ids.intersection(resources):
            self.stats[month_year][u'collections'][u'download_events'] += 1

        if resources.difference(self.resource_ids):
            self.stats[month_year][u'research'][u'download_events'] += 1

    def as_dict(self):
        '''
        Return an OrderedDict of count stats in ascending chronological order.

        :return: an OrderedDict
        '''
        return OrderedDict(sorted(self.stats.items(),
                                  key=lambda x: tuple(map(int, reversed(x[0].split(u'/'))))))


class DownloadStatistics(Statistics):
    '''
    Class used to implement the download statistics action.
    '''

    schema = statistics_downloads_schema()

    def _get_statistics(self, year=None, month=None, resource_id=None):
        '''
        Fetch the statistics.

        :param year: (optional, default: None)
        :param month: (optional, default: None)
        :param resource_id: (optional, default: None)
        :returns: dict of stats
        '''
        monthly_stats = MonthlyStats(month, year, resource_id)
        self.add_ckanpackager_stats(monthly_stats)
        self.add_versioned_datastore_download_stats(monthly_stats)
        stats = monthly_stats.as_dict()

        # if a resource_id has been specified, only return the ckanpackager/vdd stats sources as the
        # other stats aren't filterable by resource ID
        if resource_id:
            return stats
        else:
            backfill = self.backfill_stats(u'data-portal-backfill.json', year, month)
            result = self.merge(stats, backfill)
            # Merge in the GBIF stats
            for k, v in self.gbif_stats(year, month).items():
                result.setdefault(k, default={})
                result[k][u'gbif'] = v
            return result

    @staticmethod
    def gbif_stats(year=None, month=None):
        '''
        Get GBIF download stats

        :param year: (optional, default: None)
        :param month: (optional, default: None)
        :returns: dict of GBIF stats
        '''
        stats = OrderedDict()

        year_part = sql.func.date_part(u'year', GBIFDownload.date).label(u'year')
        month_part = sql.func.date_part(u'month', GBIFDownload.date).label(u'month')

        rows = model.Session.query(
            sql.func.concat(month_part, u'/', year_part).label(u'date'),
            sql.func.sum(GBIFDownload.count).label(u'records'),
            sql.func.count().label(u'download_events')
        ).group_by(year_part, month_part)

        if year:
            rows = rows.filter(sql.extract(u'year', GBIFDownload.date) == year)
        if month:
            rows = rows.filter(sql.extract(u'month', GBIFDownload.date) == month)

        rows = rows.order_by(month_part, year_part).all()

        for row in rows:
            stats[row.date] = {
                u'records': int(row.records if row.records is not None else 0),
                u'download_events':
                    int(row.download_events if row.download_events is not None else 0)
            }

        return stats

    @staticmethod
    def add_ckanpackager_stats(monthly_stats):
        '''
        Updates the given MonthlyStats object with the ckan packager download stats.

        Note: this function used to aggregate the statistics in the database using sql, however this
        changed when the versioned datastore download stats were added and now it's all done in
        Python. This is because the versioned datastore download stats are more complicated to parse
        and aggregate as the record counts are stored in a JSONB column using the resource ids as
        keys and the counts as values. Creating an SQL query to aggregate this would probably have
        been possible but it would have been horrible to maintain and therefore handling it in
        python made more sense. To then avoid having two completely different aggregation mechanisms
        in the same area I decided to switch the ckan packager stats aggregation over to python too.

        :param monthly_stats: a MonthlyStats object
        '''
        for row in model.Session.query(CKANPackagerStat):
            count = int(row.count) if row.count is not None else 0
            monthly_stats.add(row.inserted_on, row.resource_id, count)

    @staticmethod
    def add_versioned_datastore_download_stats(monthly_stats):
        '''
        Updates the given MonthlyStats object with the versioned datastore download stats. Only
        "complete" downloads are counted. Note that downloads that error out don't get the state of
        "complete", they get "failed", however to avoid creating a subtle dependency on versioned
        datastore logic in a completely different extension we check the error column is empty too.

        :param monthly_stats: a MonthlyStats object
        '''
        for download in model.Session.query(DatastoreDownload)\
                .filter(DatastoreDownload.state == state_complete) \
                .filter(DatastoreDownload.error.is_(None)):
            monthly_stats.add_all(download.created, download.resource_totals)

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
            backfill_data = {k: v for k, v in backfill_data.items() if k == str(year)}
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
        '''
        Fills gaps in stats_1 with data from stats_2.

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
