# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


import json
from collections import OrderedDict, defaultdict
from datetime import datetime as dt
from operator import itemgetter
from typing import Optional, Set

import ckan.model as model
from beaker.cache import cache_region, region_invalidate
from ckan.plugins import toolkit
from importlib_resources import files
from sqlalchemy import sql

from ckanext.statistics.model.ckanpackager import CKANPackagerStat
from ckanext.versioned_datastore.model.downloads import CoreFileRecord, DownloadRequest

from ..lib.gbif_api import get_gbif_stats
from ..lib.statistics import Statistics

backfill_filename = 'data-portal-backfill.json'


class DownloadStatistics(Statistics):
    """
    Class used to implement the download statistics action.
    """

    collection_resource_ids: Optional[Set[str]] = set(
        toolkit.config.get('ckanext.statistics.resource_ids', '').split(' ')
    )

    def get(self, year=None, month=None, resource_id=None):
        """
        Fetch the statistics.

        :param year: get stats from this year only (optional, default: None)
        :param month: get stats from this month only (optional, default: None)
        :param resource_id: get stats for this resource only (optional, default: None)
        :returns: dict of stats
        """
        today = dt.now()

        if year and (
            year > today.year or (year == today.year and month and month > today.month)
        ):
            raise toolkit.ValidationError('Date is in the future')

        current_key = self._date_format(today)
        current_only = year == today.year and (month == today.month or today.month == 1)
        current_included = (
            current_only
            or (year == today.year and month is None)
            or (year is None and month == today.month)
            or (year is None and month is None)
        )

        sources = []

        # if we're getting anything other than just the current month, get that first
        if not current_only:
            sources.append(self._get_ckanpackager(year, month, resource_id))
            sources.append(self._get_vds_download(year, month, resource_id))

            # if no resource_id has been specified we can add the backfill and gbif
            # stats as they aren't filterable by resource ID
            if not resource_id:
                sources.append(self._get_gbif(year, month))
                sources.append(self._get_backfill(backfill_filename, year, month))

        # if current month is included
        if current_included:
            # delete current month from sources
            for source in sources:
                try:
                    del source[current_key]
                except KeyError:
                    continue

            # invalidate cache for current month
            self._invalidate_cache(today.year, today.month, resource_id)

            # refresh stats for the current month
            sources.append(self._get_ckanpackager(today.year, today.month, resource_id))
            sources.append(self._get_vds_download(today.year, today.month, resource_id))
            if not resource_id:
                sources.append(self._get_gbif(today.year, today.month))
                sources.append(
                    self._get_backfill(backfill_filename, today.year, today.month)
                )

        sources.append(
            self._get_empties([k for src in sources for k in src.keys()], year, month)
        )

        def _combine(*items):
            not_null_items = [i for i in items if i is not None]
            if not not_null_items:
                return None
            if len(not_null_items) == 1 and not isinstance(not_null_items[0], dict):
                return not_null_items[0]
            if len(set([type(i) for i in not_null_items])) > 1:
                raise ValueError('Cannot combine different types.')
            if isinstance(not_null_items[0], dict):
                combined = {}
                for k in set([ik for i in not_null_items for ik in i.keys()]):
                    combined[k] = _combine(*[i.get(k) for i in not_null_items])
                return OrderedDict(sorted(combined.items(), key=itemgetter(0)))
            if isinstance(not_null_items[0], int):
                return sum(not_null_items)
            else:
                raise Exception('Unable to combine.')

        stats = OrderedDict(
            sorted(
                _combine(*sources).items(),
                key=lambda x: tuple(map(int, reversed(x[0].split('/')))),
            )
        )

        return stats

    @classmethod
    def resource_type(cls, resource_id):
        """
        Returns the resource type (collections or research). Very simple set check as a
        method for convenience.

        :param resource_id: the ID of the resource to check
        :returns: 'collections' or 'research'
        """
        return (
            'collections' if resource_id in cls.collection_resource_ids else 'research'
        )

    @staticmethod
    def _date_format(date=None, year=None, month=None):
        """
        Returns a "month/year" string from year and month or full datetime object. Pass
        either year and month OR date.

        :param date: the full date (optional, default: None)
        :param year: the year (optional, default: None)
        :param month: the month (optional, default: None)
        :returns: datestring
        """
        if date:
            return date.strftime('%-m/%Y')
        elif year and month:
            return f'{month}/{year}'
        raise ValueError

    @staticmethod
    def _init_stats_dict():
        """
        Returns the standard format for a single month's entry.

        Useful for initialising defaultdicts.
        """
        return {
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

    @cache_region('statistics_long', 'dl_stats_ckanpackager')
    def _get_ckanpackager(self, year=None, month=None, resource_id=None):
        """
        Gets ckanpackager download stats.

        :param year: stats from this year only (optional, default: None)
        :param month: stats from this month only (optional, default: None)
        :param resource_id: stats for this resource only (optional, default: None)
        :returns: dict of stats
        """
        filters = []
        if year is not None:
            filters.append((sql.extract('year', CKANPackagerStat.inserted_on) == year))
        if month is not None:
            filters.append(
                (sql.extract('month', CKANPackagerStat.inserted_on) == month)
            )
        if resource_id is not None:
            filters.append((CKANPackagerStat.resource_id == resource_id))

        stats_dict = defaultdict(self._init_stats_dict)
        for download in model.Session.query(CKANPackagerStat).filter(*filters):
            count = int(download.count) if download.count is not None else 0
            key = self._date_format(date=download.inserted_on)
            resource_type = self.resource_type(download.resource_id)
            stats_dict[key][resource_type]['records'] += count
            stats_dict[key][resource_type]['download_events'] += 1
        return dict(stats_dict)

    @cache_region('statistics_long', 'dl_stats_vds_download')
    def _get_vds_download(self, year=None, month=None, resource_id=None):
        """
        Gets versioned datastore download stats.

        :param year: stats from this year only (optional, default: None)
        :param month: stats from this month only (optional, default: None)
        :param resource_id: stats for this resource only (optional, default: None)
        :returns: dict of stats
        """
        base_query = model.Session.query(DownloadRequest)
        filters = [(DownloadRequest.state == DownloadRequest.state_complete)]
        if year is not None:
            filters.append((sql.extract('year', DownloadRequest.created) == year))
        if month is not None:
            filters.append((sql.extract('month', DownloadRequest.created) == month))
        if resource_id is not None:
            base_query = base_query.join(CoreFileRecord)
            filters.append(
                (CoreFileRecord.resource_ids_and_versions.op('?')(resource_id))
            )

        stats_dict = defaultdict(self._init_stats_dict)
        for download in base_query.filter(*filters):
            key = self._date_format(date=download.created)
            has_research = False
            has_collections = False
            for rid, rc in download.core_record.resource_totals.items():
                resource_type = self.resource_type(rid)
                if resource_type == 'research':
                    has_research = True
                elif resource_type == 'collections':
                    has_collections = True
                stats_dict[key][resource_type]['records'] += rc
            # if a download contains both research and collections data, it gets
            # counted twice
            if has_research:
                stats_dict[key]['research']['download_events'] += 1
            if has_collections:
                stats_dict[key]['collections']['download_events'] += 1
        return dict(stats_dict)

    @cache_region('statistics_long', 'dl_stats_gbif')
    def _get_gbif(self, year=None, month=None):
        """
        Gets GBIF download stats.

        :param year: stats from this year only (optional, default: None)
        :param month: stats from this month only (optional, default: None)
        :returns: dict of stats
        """
        stats_dict = defaultdict(self._init_stats_dict)
        for result in get_gbif_stats(year, month):
            key = self._date_format(year=result['year'], month=result['month'])
            stats_dict[key]['gbif']['records'] += result['records']
            stats_dict[key]['gbif']['download_events'] += result['events']
        return dict(stats_dict)

    @cache_region('statistics_long', 'dl_stats_backfill')
    def _get_backfill(self, filename, year=None, month=None):
        """
        Gets stats from a static file.

        :param filename: the name of the json file containing the statistics
        :param year: stats from this year only (optional, default: None)
        :param month: stats from this month only (optional, default: None)
        :returns: dict of stats
        """
        if filename is None:
            return

        backfill_file = files('ckanext.statistics.data').joinpath(filename)
        backfill_data = json.loads(backfill_file.read_text())

        query_data = backfill_data
        if year:
            query_data = {year: query_data.get(str(year), {})}
        # for month it's easier to just iterate

        stats_dict = {}
        for y, months in query_data.items():
            for m, stats in months.items():
                if month and m != str(month):
                    continue
                key = self._date_format(year=y, month=m)
                stats_dict[key] = stats
        return stats_dict

    def _get_empties(self, existing_keys, year=None, month=None):
        """
        Get "empty" months to fill in gaps.

        :param existing_keys: keys already provided by other sources
        :param year: stats from this year only (optional, default: None)
        :param month: stats from this month only (optional, default: None)
        :returns: dict of stats
        """
        today = dt.now()
        if year and month:
            return {self._date_format(year=year, month=month): self._init_stats_dict()}
        if year:
            return {
                self._date_format(year=year, month=ix + 1): self._init_stats_dict()
                for ix in range(12)
            }

        # find the years we've already got data for (current year if none)
        existing_years = sorted([int(k.split('/')[1]) for k in existing_keys])
        first_year = existing_years[0] if existing_years else today.year
        months = [month] if month else [ix + 1 for ix in range(12)]
        empties = {}
        for y in range(first_year, today.year + 1):
            for m in months:
                if y >= today.year and m >= today.month:
                    continue
                empties[self._date_format(year=y, month=m)] = self._init_stats_dict()
        return empties

    def _invalidate_cache(self, year, month, resource_id):
        """
        Invalidate the beaker cache for all the _get functions for the given year,
        month, and resource ID.

        :param year: stats from this year only (optional, default: None)
        :param month: stats from this month only (optional, default: None)
        :param resource_id: stats for this resource only (optional, default: None)
        """
        ym = [year, month]
        to_invalidate = [
            (self._get_ckanpackager, 'dl_stats_ckanpackager', [*ym, resource_id]),
            (self._get_vds_download, 'dl_stats_vds_download', [*ym, resource_id]),
            (self._get_gbif, 'dl_stats_gbif', ym),
            (self._get_backfill, 'dl_stats_backfill', [backfill_filename, *ym]),
        ]
        for func, func_name, func_args in to_invalidate:
            region_invalidate(
                func,
                'statistics_long',
                func_name,
                *func_args,
            )
