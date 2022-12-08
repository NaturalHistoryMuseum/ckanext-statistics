# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


import json
from collections import OrderedDict, defaultdict

from importlib_resources import files
from sqlalchemy import sql

import ckan.model as model
from ckan.plugins import toolkit
from ckanext.ckanpackager.model.stat import CKANPackagerStat
from ckanext.versioned_datastore.model.downloads import (
    DatastoreDownload,
    state_complete,
)
from ..lib.statistics import Statistics
from ..logic.schema import statistics_downloads_schema
from ..model.gbif_download import GBIFDownload

backfill_filename = 'data-portal-backfill.json'


class MonthlyStats(object):
    """
    Class used to keep track of the monthly download counts from multiple sources.
    """

    def __init__(self, month=None, year=None, resource_id=None):
        '''
        :param month: if passed, only this month will be counted (defaults to None)
        :param year: if passed, only this year will be counted (defaults to None)
        :param resource_id: if passed, only this resource will be counted (defaults to None)
        '''
        self.month = int(month) if month is not None else None
        self.year = int(year) if year is not None else None
        self.resource_id = resource_id

        self.stats = defaultdict(
            lambda: {
                'collections': {
                    'records': 0,
                    'download_events': 0,
                },
                'research': {
                    'records': 0,
                    'download_events': 0,
                },
                'gbif': {
                    'records': 0,
                    'download_events': 0,
                },
            }
        )
        # extract the collection resource ids from the config
        self.collection_resource_ids = toolkit.config.get(
            'ckanext.statistics.resource_ids', set()
        )
        if self.collection_resource_ids:
            self.collection_resource_ids = set(self.collection_resource_ids.split(' '))

    def add(self, date, resource_id, count):
        """
        Updates the stats with the download event information for the given resource and
        count at the given date.

        :param date: the date of the download event
        :param resource_id: the resource downloaded
        :param count: the number of records downloaded
        """
        self.add_all(date, {resource_id: count})

    def add_all(self, date, resource_counts):
        """
        Updates the stats with the download event information for the given resources
        and counts at the given date. This function filters out information about
        months/years/resources we're not interested in based on the parameters passed
        during the construction of this object.

        :param date: the date of the download event
        :param resource_counts: a dict of resource ids -> counts
        """
        month_year = date.strftime('%-m/%Y')
        month, year = map(int, month_year.split('/'))

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
            if resource_id in self.collection_resource_ids:
                resource_type = 'collections'
            else:
                resource_type = 'research'
            self.stats[month_year][resource_type]['records'] += count

        resources = set(resource_counts.keys())
        if self.collection_resource_ids.intersection(resources):
            self.stats[month_year]['collections']['download_events'] += 1

        if resources.difference(self.collection_resource_ids):
            self.stats[month_year]['research']['download_events'] += 1

    def update_from_backfill(self, month, year, stats):
        """
        Adds the given stats for the given month and year to our stats dict. The month
        and year filters will be applied if applicable.

        :param month: the month
        :param year: the year
        :param stats: the stats in a dict, the format of this dict must match a month/year entry in
                      the self.stats dict
        """
        if self.month is not None and self.month != int(month):
            return
        if self.year is not None and self.year != int(year):
            return

        month_year = f'{month}/{year}'
        for group in ('collections', 'research'):
            for count_name in ('download_events', 'records'):
                self.stats[month_year][group][count_name] += stats.get(group, {}).get(
                    count_name, 0
                )

    def update_from_gbif(self, month, year, records, download_events):
        """
        Add gbif stats to this stats object.

        :param month: the month
        :param year: the year
        :param records: the number of records downloaded
        :param download_events: the number of download events
        """
        month = int(month)
        year = int(year)
        if self.month is not None and self.month != month:
            return
        if self.year is not None and self.year != year:
            return

        month_year = f'{month}/{year}'
        records = int(records if records is not None else 0)
        download_events = int(download_events if download_events is not None else 0)
        self.stats[month_year]['gbif']['records'] += records
        self.stats[month_year]['gbif']['download_events'] += download_events

    def as_dict(self):
        """
        Return an OrderedDict of count stats in ascending chronological order.

        :return: an OrderedDict
        """
        return OrderedDict(
            sorted(
                self.stats.items(),
                key=lambda x: tuple(map(int, reversed(x[0].split('/')))),
            )
        )


class DownloadStatistics(Statistics):
    """
    Class used to implement the download statistics action.
    """

    schema = statistics_downloads_schema()

    def _get_statistics(self, year=None, month=None, resource_id=None):
        """
        Fetch the statistics.

        :param year: (optional, default: None)
        :param month: (optional, default: None)
        :param resource_id: (optional, default: None)
        :returns: dict of stats
        """
        monthly_stats = MonthlyStats(month, year, resource_id)
        self.add_ckanpackager_stats(monthly_stats)
        self.add_versioned_datastore_download_stats(monthly_stats)

        # if no resource_id has been specified we can add the backfill and gbif stats as they aren't
        # filterable by resource ID
        if not resource_id:
            self.add_backfill_stats(backfill_filename, monthly_stats)
            self.add_gbif_stats(monthly_stats, year, month)

        return monthly_stats.as_dict()

    @staticmethod
    def add_gbif_stats(monthly_stats, year=None, month=None):
        """
        Add the GBIF download stats to the monthly stats object.

        :param monthly_stats: the MonthlyStats object to add the GBIF stats to
        :param year: (optional, default: None)
        :param month: (optional, default: None)
        """
        year_part = sql.func.date_part('year', GBIFDownload.date).label('year')
        month_part = sql.func.date_part('month', GBIFDownload.date).label('month')

        rows = model.Session.query(
            month_part,
            year_part,
            sql.func.sum(GBIFDownload.count).label('records'),
            sql.func.count().label('download_events'),
        ).group_by(year_part, month_part)

        if year:
            rows = rows.filter(sql.extract('year', GBIFDownload.date) == year)
        if month:
            rows = rows.filter(sql.extract('month', GBIFDownload.date) == month)

        for row in rows:
            monthly_stats.update_from_gbif(
                row.month, row.year, row.records, row.download_events
            )

    @staticmethod
    def add_ckanpackager_stats(monthly_stats):
        """
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
        """
        for row in model.Session.query(CKANPackagerStat):
            count = int(row.count) if row.count is not None else 0
            monthly_stats.add(row.inserted_on, row.resource_id, count)

    @staticmethod
    def add_versioned_datastore_download_stats(monthly_stats):
        """
        Updates the given MonthlyStats object with the versioned datastore download
        stats. Only "complete" downloads are counted. Note that downloads that error out
        don't get the state of "complete", they get "failed", however to avoid creating
        a subtle dependency on versioned datastore logic in a completely different
        extension we check the error column is empty too.

        :param monthly_stats: a MonthlyStats object
        """
        for download in (
            model.Session.query(DatastoreDownload)
            .filter(DatastoreDownload.state == state_complete)
            .filter(DatastoreDownload.error.is_(None))
        ):
            monthly_stats.add_all(download.created, download.resource_totals)

    @staticmethod
    def add_backfill_stats(filename, monthly_stats):
        """
        Updates the MonthlyStats object with static data from a json file that can be
        used to fill gaps in the API's returned statistics.

        :param filename: the name of the json file containing the statistics
        :param monthly_stats: a MonthlyStats object
        """
        if filename is None:
            return

        backfill_file = files('ckanext.statistics.data').joinpath(filename)
        backfill_data = json.loads(backfill_file.read_text())

        for year in backfill_data:
            for month, stats in backfill_data[year].items():
                monthly_stats.update_from_backfill(month, year, stats)
