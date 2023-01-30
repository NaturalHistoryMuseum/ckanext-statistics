# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from collections import OrderedDict
from datetime import datetime

import pytest
from ckanext.ckanpackager.model.stat import CKANPackagerStat, ckanpackager_stats_table
from ckanext.statistics.lib.download_statistics import DownloadStatistics, MonthlyStats
from ckanext.statistics.model.gbif_download import GBIFDownload, gbif_downloads_table
from ckanext.versioned_datastore.model import stats, slugs, details, downloads
from ckanext.versioned_datastore.model.downloads import (
    DownloadRequest,
    CoreFileRecord,
    DerivativeFileRecord,
)
from unittest.mock import MagicMock, call


class TestMonthlyStats(object):
    def test_add_all_no_filters_all_research(self):
        date = datetime(2020, 1, 1)
        resource_counts = {
            'resource1': 10002,
            'resource2': 51,
        }
        monthly_stats = MonthlyStats()
        monthly_stats.add_all(date, resource_counts)
        assert monthly_stats.stats['1/2020']['research']['records'] == 10002 + 51
        assert monthly_stats.stats['1/2020']['research']['download_events'] == 1
        assert monthly_stats.stats['1/2020']['collections']['records'] == 0
        assert monthly_stats.stats['1/2020']['collections']['download_events'] == 0

    @pytest.mark.ckan_config('ckanext.statistics.resource_ids', 'resource1 resource2')
    def test_add_all_no_filters_all_collections(self):
        date = datetime(2020, 1, 1)
        resource_counts = {
            'resource1': 10002,
            'resource2': 51,
        }
        monthly_stats = MonthlyStats()
        monthly_stats.add_all(date, resource_counts)
        assert monthly_stats.stats['1/2020']['collections']['records'] == 10002 + 51
        assert monthly_stats.stats['1/2020']['collections']['download_events'] == 1
        assert monthly_stats.stats['1/2020']['research']['records'] == 0
        assert monthly_stats.stats['1/2020']['research']['download_events'] == 0

    @pytest.mark.ckan_config('ckanext.statistics.resource_ids', 'cresource2')
    def test_add_all_no_filters_mixed(self):
        date = datetime(2020, 1, 1)
        resource_counts = {
            'resource1': 10002,
            'cresource2': 51,
        }
        monthly_stats = MonthlyStats()
        monthly_stats.add_all(date, resource_counts)
        assert monthly_stats.stats['1/2020']['collections']['records'] == 51
        assert monthly_stats.stats['1/2020']['collections']['download_events'] == 1
        assert monthly_stats.stats['1/2020']['research']['records'] == 10002
        assert monthly_stats.stats['1/2020']['research']['download_events'] == 1

    @pytest.mark.ckan_config('ckanext.statistics.resource_ids', 'cresource2')
    def test_add_all_month_filter_mixed(self):
        date1 = datetime(2020, 1, 1)
        resource_counts1 = {
            'resource1': 10002,
            'cresource2': 51,
        }
        date2 = datetime(2020, 3, 1)
        resource_counts2 = {
            'resource1': 29,
            'cresource2': 38290,
        }
        monthly_stats = MonthlyStats(month=3)
        monthly_stats.add_all(date1, resource_counts1)
        monthly_stats.add_all(date2, resource_counts2)
        assert '1/2020' not in monthly_stats.stats
        assert monthly_stats.stats['3/2020']['research']['records'] == 29
        assert monthly_stats.stats['3/2020']['research']['download_events'] == 1
        assert monthly_stats.stats['3/2020']['collections']['records'] == 38290
        assert monthly_stats.stats['3/2020']['collections']['download_events'] == 1

    @pytest.mark.ckan_config('ckanext.statistics.resource_ids', 'cresource2')
    def test_add_all_year_filter_mixed(self):
        date1 = datetime(2019, 1, 1)
        resource_counts1 = {
            'resource1': 10002,
            'cresource2': 51,
        }
        date2 = datetime(2020, 1, 1)
        resource_counts2 = {
            'resource1': 29,
            'cresource2': 38290,
        }
        monthly_stats = MonthlyStats(year=2019)
        monthly_stats.add_all(date1, resource_counts1)
        monthly_stats.add_all(date2, resource_counts2)
        assert '1/2020' not in monthly_stats.stats
        assert monthly_stats.stats['1/2019']['research']['records'] == 10002
        assert monthly_stats.stats['1/2019']['research']['download_events'] == 1
        assert monthly_stats.stats['1/2019']['collections']['records'] == 51
        assert monthly_stats.stats['1/2019']['collections']['download_events'] == 1

    @pytest.mark.ckan_config('ckanext.statistics.resource_ids', 'cresource2')
    def test_add_all_resource_filter_mixed(self):
        date1 = datetime(2019, 1, 1)
        resource_counts1 = {
            'resource1': 10002,
            'cresource2': 51,
        }
        date2 = datetime(2020, 1, 1)
        resource_counts2 = {
            'resource1': 29,
            'cresource2': 38290,
        }
        monthly_stats = MonthlyStats(resource_id='resource1')
        monthly_stats.add_all(date1, resource_counts1)
        monthly_stats.add_all(date2, resource_counts2)
        assert monthly_stats.stats['1/2019']['research']['records'] == 10002
        assert monthly_stats.stats['1/2019']['research']['download_events'] == 1
        assert monthly_stats.stats['1/2019']['collections']['records'] == 0
        assert monthly_stats.stats['1/2019']['collections']['download_events'] == 0
        assert monthly_stats.stats['1/2020']['research']['records'] == 29
        assert monthly_stats.stats['1/2020']['research']['download_events'] == 1
        assert monthly_stats.stats['1/2020']['collections']['records'] == 0
        assert monthly_stats.stats['1/2020']['collections']['download_events'] == 0

    @pytest.mark.ckan_config('ckanext.statistics.resource_ids', 'cresource2 resource2')
    def test_add_all_complex_filter_mixed(self):
        date = datetime(2019, 6, 1)
        resource_counts = {
            'resource1': 10,
            'cresource2': 51,
            'resource2': 19,
        }
        monthly_stats = MonthlyStats(month=6, year=2019, resource_id='resource2')
        monthly_stats.add_all(date, resource_counts)
        assert monthly_stats.stats['6/2019']['research']['records'] == 0
        assert monthly_stats.stats['6/2019']['research']['download_events'] == 0
        assert monthly_stats.stats['6/2019']['collections']['records'] == 19
        assert monthly_stats.stats['6/2019']['collections']['download_events'] == 1

    def test_month_year_format(self):
        # currently the month/year keys are not zero padded so we might as well test that that is
        # still the case in case a developer gets refactor happy and changes it (I did this so maybe
        # this test is for me...)
        monthly_stats = MonthlyStats()
        for month in range(1, 12):
            date = datetime(2017, month, 1)
            monthly_stats.add_all(date, resource_counts=dict(resource1=10))
            month_year = '{}/2017'.format(month)
            assert monthly_stats.stats[month_year]['research']['records'] == 10
            assert monthly_stats.stats[month_year]['research']['download_events'] == 1

    def test_add(self):
        # check that add just calls add_all
        monthly_stats = MonthlyStats()
        monthly_stats.add_all = MagicMock()
        date = MagicMock()
        resource_id = MagicMock()
        count = MagicMock()
        monthly_stats.add(date, resource_id, count)
        assert monthly_stats.add_all.called
        assert monthly_stats.add_all.call_args == call(date, {resource_id: count})

    def test_as_dict(self):
        monthly_stats = MonthlyStats()
        monthly_stats.add(datetime(2017, 4, 1), 'resource1', 29)
        monthly_stats.add(datetime(2017, 4, 20), 'resource1', 39)
        monthly_stats.add(datetime(2013, 6, 18), 'resource2', 1000)
        monthly_stats.add(datetime(2013, 1, 8), 'resource5', 55)
        monthly_stats.add(datetime(2013, 11, 4), 'resource2', 1000)
        monthly_stats.add(datetime(2020, 10, 10), 'resource4', 92)

        stats = monthly_stats.as_dict()
        assert isinstance(stats, OrderedDict)
        assert list(stats.keys()) == [
            '1/2013',
            '6/2013',
            '11/2013',
            '4/2017',
            '10/2020',
        ]

    def test_update_from_backfill_no_previous_data(self):
        monthly_stats = MonthlyStats()
        monthly_stats.update_from_backfill(
            '10',
            '2018',
            {
                'collections': {'download_events': 102, 'records': 1029},
                'research': {'download_events': 4, 'records': 902832},
            },
        )
        assert monthly_stats.stats['10/2018']['collections']['download_events'] == 102
        assert monthly_stats.stats['10/2018']['collections']['records'] == 1029
        assert monthly_stats.stats['10/2018']['research']['download_events'] == 4
        assert monthly_stats.stats['10/2018']['research']['records'] == 902832

    @pytest.mark.ckan_config('ckanext.statistics.resource_ids', 'resource1')
    def test_update_from_backfill_with_previous_data(self):
        monthly_stats = MonthlyStats()
        # this is a collection resource
        monthly_stats.add(datetime(2018, 10, 1), 'resource1', 20)
        # this isn't a collection resource
        monthly_stats.add(datetime(2018, 10, 1), 'resource2', 15)
        # update from the backfill
        monthly_stats.update_from_backfill(
            '10',
            '2018',
            {
                'collections': {
                    'download_events': 3,
                    'records': 10004,
                },
                'research': {
                    'download_events': 5829,
                    'records': 32894932,
                },
            },
        )
        assert monthly_stats.stats['10/2018']['collections']['download_events'] == 3 + 1
        assert monthly_stats.stats['10/2018']['collections']['records'] == 10004 + 20
        assert monthly_stats.stats['10/2018']['research']['download_events'] == 5829 + 1
        assert monthly_stats.stats['10/2018']['research']['records'] == 32894932 + 15

    def test_update_from_backfill_with_filters(self):
        monthly_stats = MonthlyStats(month=10, year=2018)
        monthly_stats.update_from_backfill(
            '10',
            '2018',
            {
                'collections': {
                    'download_events': 3,
                    'records': 10004,
                },
                'research': {
                    'download_events': 5829,
                    'records': 32894932,
                },
            },
        )
        monthly_stats.update_from_backfill(
            '11',
            '2018',
            {
                'collections': {
                    'download_events': 3,
                    'records': 10004,
                },
                'research': {
                    'download_events': 5829,
                    'records': 32894932,
                },
            },
        )
        monthly_stats.update_from_backfill(
            '11',
            '2017',
            {
                'collections': {
                    'download_events': 3,
                    'records': 10004,
                },
                'research': {
                    'download_events': 5829,
                    'records': 32894932,
                },
            },
        )
        assert '10/2018' in monthly_stats.stats
        assert '11/2018' not in monthly_stats.stats
        assert '11/2017' not in monthly_stats.stats

    def test_update_from_gbif(self):
        monthly_stats = MonthlyStats()
        monthly_stats.update_from_gbif(10, 2018, 83, 4)
        monthly_stats.update_from_gbif(10, 2018, 18, 5)
        assert monthly_stats.stats['10/2018']['gbif']['download_events'] == 4 + 5
        assert monthly_stats.stats['10/2018']['gbif']['records'] == 83 + 18

    def test_update_from_gbif_with_filters(self):
        monthly_stats = MonthlyStats(month=10, year=2018)
        monthly_stats.update_from_gbif(10, 2019, 2389, 223)
        monthly_stats.update_from_gbif(4, 2012, 100, 28)
        monthly_stats.update_from_gbif(10, 2018, 8344, 40)
        monthly_stats.update_from_gbif(10, 2018, 40, 1)
        assert monthly_stats.stats['10/2018']['gbif']['download_events'] == 40 + 1
        assert monthly_stats.stats['10/2018']['gbif']['records'] == 8344 + 40
        assert '10/2019' not in monthly_stats.stats
        assert '4/2012' not in monthly_stats.stats


@pytest.fixture
def with_needed_tables(reset_db):
    """
    Simple fixture which resets the database and creates the tables we need from this
    extension plus the versioned datastore and ckanpackager extensions.
    """
    reset_db()
    tables = [
        stats.import_stats_table,
        slugs.datastore_slugs_table,
        details.datastore_resource_details_table,
        downloads.datastore_downloads_core_files_table,
        downloads.datastore_downloads_derivative_files_table,
        downloads.datastore_downloads_requests_table,
        ckanpackager_stats_table,
        gbif_downloads_table,
    ]
    # create the tables if they don't exist
    for table in tables:
        if not table.exists():
            table.create()


@pytest.mark.ckan_config('ckan.plugins', 'statistics versioned_datastore ckanpackager')
@pytest.mark.usefixtures('with_needed_tables', 'with_plugins')
@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
class TestDownloadStatistics(object):
    def test_get_statistics_no_filters_calls_the_right_functions(self):
        dl_stats = DownloadStatistics(MagicMock(), MagicMock())

        dl_stats.add_ckanpackager_stats = MagicMock()
        dl_stats.add_versioned_datastore_download_stats = MagicMock()
        dl_stats.add_backfill_stats = MagicMock()
        dl_stats.add_gbif_stats = MagicMock()

        dl_stats._get_statistics()

        assert dl_stats.add_ckanpackager_stats.call_count == 1
        assert dl_stats.add_versioned_datastore_download_stats.call_count == 1
        assert dl_stats.add_backfill_stats.call_count == 1
        assert dl_stats.add_gbif_stats.call_count == 1

    def test_get_statistics_with_filters_calls_the_right_functions(self):
        dl_stats = DownloadStatistics(MagicMock(), MagicMock())

        dl_stats.add_ckanpackager_stats = MagicMock()
        dl_stats.add_versioned_datastore_download_stats = MagicMock()
        dl_stats.add_backfill_stats = MagicMock()
        dl_stats.add_gbif_stats = MagicMock()

        dl_stats._get_statistics(resource_id=MagicMock())

        assert dl_stats.add_ckanpackager_stats.call_count == 1
        assert dl_stats.add_versioned_datastore_download_stats.call_count == 1
        # shouldn't call these ones cause they can't be filtered by resource id
        assert dl_stats.add_backfill_stats.call_count == 0
        assert dl_stats.add_gbif_stats.call_count == 0

    def test_add_gbif_stats(self):
        downloads = [
            GBIFDownload(doi='doi1', date=datetime(2019, 8, 22), count=18),
            GBIFDownload(doi='doi2', date=datetime(2019, 8, 17), count=3),
            GBIFDownload(doi='doi3', date=datetime(2018, 8, 30), count=15),
            GBIFDownload(doi='doi4', date=datetime(2018, 8, 21), count=289),
            GBIFDownload(doi='doi5', date=datetime(2019, 2, 11), count=490),
            GBIFDownload(doi='doi6', date=datetime(2019, 2, 5), count=1),
            GBIFDownload(doi='doi7', date=datetime(2013, 1, 1), count=29000),
        ]
        for download in downloads:
            download.save()

        dl_stats = DownloadStatistics(MagicMock(), MagicMock())
        monthly_stats = MagicMock()
        dl_stats.add_gbif_stats(monthly_stats)

        calls = monthly_stats.update_from_gbif.call_args_list
        assert len(calls) == 4
        assert call(1, 2013, 29000, 1) in calls
        assert call(8, 2018, 15 + 289, 2) in calls
        assert call(2, 2019, 490 + 1, 2) in calls
        assert call(8, 2019, 18 + 3, 2) in calls

    def test_add_ckanpackager_stats(self):
        downloads = [
            CKANPackagerStat(
                inserted_on=datetime(2018, 4, 1), resource_id='resource1', count=389
            ),
            CKANPackagerStat(
                inserted_on=datetime(2019, 1, 1), resource_id='resource2', count=910
            ),
            CKANPackagerStat(
                inserted_on=datetime(2011, 12, 1), resource_id='resource3', count=86
            ),
            CKANPackagerStat(
                inserted_on=datetime(2011, 12, 1), resource_id='blarp', count=None
            ),
        ]
        for download in downloads:
            download.save()

        dl_stats = DownloadStatistics(MagicMock(), MagicMock())
        monthly_stats = MagicMock()
        dl_stats.add_ckanpackager_stats(monthly_stats)

        calls = monthly_stats.add.call_args_list
        assert len(calls) == 4
        assert call(datetime(2018, 4, 1), 'resource1', 389) in calls
        assert call(datetime(2019, 1, 1), 'resource2', 910) in calls
        assert call(datetime(2011, 12, 1), 'resource3', 86) in calls
        # the None count should be converted to 0
        assert call(datetime(2011, 12, 1), 'blarp', 0) in calls

    def test_add_versioned_datastore_download_stats(self):

        core_record_kwargs = {
            'query': {},
            'query_version': 'v12.4.9',
            'total': 1,
            'field_counts': {},
        }

        core_record_1 = CoreFileRecord(
            resource_ids_and_versions={'resource1': 1, 'resource2': 1},
            query_hash='abcd',
            resource_hash='abcd',
            modified=datetime(2019, 1, 1),
            resource_totals={'resource1': 100, 'resource2': 32},
            **core_record_kwargs
        )
        core_record_1.save()

        core_record_2 = CoreFileRecord(
            resource_ids_and_versions={'resource1': 1},
            query_hash='efgh',
            resource_hash='efgh',
            modified=datetime(2018, 5, 10),
            resource_totals={'resource1': 4},
            **core_record_kwargs
        )
        core_record_2.save()

        core_record_3 = CoreFileRecord(
            resource_ids_and_versions={'resource3': 1},
            query_hash='ijkl',
            resource_hash='ijkl',
            modified=datetime(2018, 4, 14),
            resource_totals={'resource3': 189},
            **core_record_kwargs
        )
        core_record_3.save()

        downloads = [
            DownloadRequest(
                created=datetime(2019, 1, 1),
                state=DownloadRequest.state_complete,
                core_id=core_record_1.id,
            ),
            DownloadRequest(
                created=datetime(2019, 3, 30),
                state=DownloadRequest.state_complete,
                core_id=core_record_1.id,
            ),
            DownloadRequest(
                created=datetime(2018, 5, 10),
                state=DownloadRequest.state_failed,
                message='error!',
                core_id=core_record_2.id,
            ),
            DownloadRequest(
                created=datetime(2018, 4, 14),
                state=DownloadRequest.state_packaging,
                core_id=core_record_3.id,
            ),
        ]
        for download in downloads:
            download.save()

        dl_stats = DownloadStatistics(MagicMock(), MagicMock())
        monthly_stats = MagicMock()
        dl_stats.add_versioned_datastore_download_stats(monthly_stats)

        calls = monthly_stats.add_all.call_args_list
        assert len(calls) == 2
        # only these two should come through, the others are either in error or not complete
        assert call(datetime(2019, 1, 1), {'resource1': 100, 'resource2': 32}) in calls
        assert call(datetime(2019, 3, 30), {'resource1': 100, 'resource2': 32}) in calls
