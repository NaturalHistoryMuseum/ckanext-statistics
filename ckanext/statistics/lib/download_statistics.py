# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


import json
from collections import OrderedDict, defaultdict
from typing import Optional, Set

import ckan.model as model
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
        sources = [
            self._get_ckanpackager(year, month, resource_id),
            self._get_vds_download(year, month, resource_id),
        ]

        # if no resource_id has been specified we can add the backfill and gbif stats as
        # they aren't filterable by resource ID
        if not resource_id:
            sources.append(self._get_gbif(year, month))
            sources.append(self._get_backfill(backfill_filename, year, month))

        def _combine(*items):
            not_null_items = [i for i in items if i is not None]
            if not not_null_items:
                return None
            if len(not_null_items) == 1:
                return not_null_items[0]
            if len(set([type(i) for i in not_null_items])) > 1:
                raise ValueError('Cannot combine different types.')
            if isinstance(not_null_items[0], dict):
                combined = {}
                for k in set([ik for i in not_null_items for ik in i.keys()]):
                    combined[k] = _combine(*[i.get(k) for i in not_null_items])
                return combined
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

    def _get_ckanpackager(self, year=None, month=None, resource_id=None):
        """
        Gets ckanpackager download stats.

        :param year: stats from this year only (optional, default: None)
        :param month: stats from this month only (optional, default: None)
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

    def _get_vds_download(self, year=None, month=None, resource_id=None):
        """
        Gets versioned datastore download stats.

        :param year: stats from this year only (optional, default: None)
        :param month: stats from this month only (optional, default: None)
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
            for rid, rc in download.core_record.resource_totals.items():
                resource_type = self.resource_type(rid)
                stats_dict[key][resource_type]['records'] += rc
                stats_dict[key][resource_type]['download_events'] += 1
        return dict(stats_dict)

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
