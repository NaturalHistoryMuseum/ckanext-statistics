# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from collections import OrderedDict
from contextlib import contextmanager
from datetime import datetime

from ckanext.ckanpackager.model.stat import CKANPackagerStat
from ckanext.statistics.model.gbif_download import GBIFDownload
from ckanext.versioned_datastore.model.downloads import DatastoreDownload, state_complete, \
    state_zipping
from ckantest.models import TestBase
from mock import MagicMock, patch, call
from nose.tools import assert_equal, assert_false, assert_true

from ..lib.download_statistics import DownloadStatistics, MonthlyStats


class TestMonthlyStats(object):

    @staticmethod
    @contextmanager
    def patch_collection_resources(collection_resources):
        config_mock = MagicMock(get=MagicMock(return_value=collection_resources))
        with patch(u'ckanext.statistics.lib.download_statistics.toolkit.config', config_mock):
            yield

    def test_add_all_no_filters_all_research(self):
        date = datetime(2020, 1, 1)
        resource_counts = {
            u'resource1': 10002,
            u'resource2': 51,
        }
        monthly_stats = MonthlyStats()
        monthly_stats.add_all(date, resource_counts)
        assert_equal(monthly_stats.stats[u'1/2020'][u'research'][u'records'], 10002 + 51)
        assert_equal(monthly_stats.stats[u'1/2020'][u'research'][u'download_events'], 1)
        assert_equal(monthly_stats.stats[u'1/2020'][u'collections'][u'records'], 0)
        assert_equal(monthly_stats.stats[u'1/2020'][u'collections'][u'download_events'], 0)

    def test_add_all_no_filters_all_collections(self):
        date = datetime(2020, 1, 1)
        resource_counts = {
            u'resource1': 10002,
            u'resource2': 51,
        }
        with self.patch_collection_resources(u'resource1 resource2'):
            monthly_stats = MonthlyStats()
            monthly_stats.add_all(date, resource_counts)
            assert_equal(monthly_stats.stats[u'1/2020'][u'collections'][u'records'], 10002 + 51)
            assert_equal(monthly_stats.stats[u'1/2020'][u'collections'][u'download_events'], 1)
            assert_equal(monthly_stats.stats[u'1/2020'][u'research'][u'records'], 0)
            assert_equal(monthly_stats.stats[u'1/2020'][u'research'][u'download_events'], 0)

    def test_add_all_no_filters_mixed(self):
        date = datetime(2020, 1, 1)
        resource_counts = {
            u'resource1': 10002,
            u'cresource2': 51,
        }
        with self.patch_collection_resources(u'cresource2'):
            monthly_stats = MonthlyStats()
            monthly_stats.add_all(date, resource_counts)
            assert_equal(monthly_stats.stats[u'1/2020'][u'collections'][u'records'], 51)
            assert_equal(monthly_stats.stats[u'1/2020'][u'collections'][u'download_events'], 1)
            assert_equal(monthly_stats.stats[u'1/2020'][u'research'][u'records'], 10002)
            assert_equal(monthly_stats.stats[u'1/2020'][u'research'][u'download_events'], 1)

    def test_add_all_month_filter_mixed(self):
        date1 = datetime(2020, 1, 1)
        resource_counts1 = {
            u'resource1': 10002,
            u'cresource2': 51,
        }
        date2 = datetime(2020, 3, 1)
        resource_counts2 = {
            u'resource1': 29,
            u'cresource2': 38290,
        }
        with self.patch_collection_resources(u'cresource2'):
            monthly_stats = MonthlyStats(month=3)
            monthly_stats.add_all(date1, resource_counts1)
            monthly_stats.add_all(date2, resource_counts2)
            assert_false(u'1/2020' in monthly_stats.stats)
            assert_equal(monthly_stats.stats[u'3/2020'][u'research'][u'records'], 29)
            assert_equal(monthly_stats.stats[u'3/2020'][u'research'][u'download_events'], 1)
            assert_equal(monthly_stats.stats[u'3/2020'][u'collections'][u'records'], 38290)
            assert_equal(monthly_stats.stats[u'3/2020'][u'collections'][u'download_events'], 1)

    def test_add_all_year_filter_mixed(self):
        date1 = datetime(2019, 1, 1)
        resource_counts1 = {
            u'resource1': 10002,
            u'cresource2': 51,
        }
        date2 = datetime(2020, 1, 1)
        resource_counts2 = {
            u'resource1': 29,
            u'cresource2': 38290,
        }
        with self.patch_collection_resources(u'cresource2'):
            monthly_stats = MonthlyStats(year=2019)
            monthly_stats.add_all(date1, resource_counts1)
            monthly_stats.add_all(date2, resource_counts2)
            assert_false(u'1/2020' in monthly_stats.stats)
            assert_equal(monthly_stats.stats[u'1/2019'][u'research'][u'records'], 10002)
            assert_equal(monthly_stats.stats[u'1/2019'][u'research'][u'download_events'], 1)
            assert_equal(monthly_stats.stats[u'1/2019'][u'collections'][u'records'], 51)
            assert_equal(monthly_stats.stats[u'1/2019'][u'collections'][u'download_events'], 1)

    def test_add_all_resource_filter_mixed(self):
        date1 = datetime(2019, 1, 1)
        resource_counts1 = {
            u'resource1': 10002,
            u'cresource2': 51,
        }
        date2 = datetime(2020, 1, 1)
        resource_counts2 = {
            u'resource1': 29,
            u'cresource2': 38290,
        }
        with self.patch_collection_resources(u'cresource2'):
            monthly_stats = MonthlyStats(resource_id=u'resource1')
            monthly_stats.add_all(date1, resource_counts1)
            monthly_stats.add_all(date2, resource_counts2)
            assert_equal(monthly_stats.stats[u'1/2019'][u'research'][u'records'], 10002)
            assert_equal(monthly_stats.stats[u'1/2019'][u'research'][u'download_events'], 1)
            assert_equal(monthly_stats.stats[u'1/2019'][u'collections'][u'records'], 0)
            assert_equal(monthly_stats.stats[u'1/2019'][u'collections'][u'download_events'], 0)
            assert_equal(monthly_stats.stats[u'1/2020'][u'research'][u'records'], 29)
            assert_equal(monthly_stats.stats[u'1/2020'][u'research'][u'download_events'], 1)
            assert_equal(monthly_stats.stats[u'1/2020'][u'collections'][u'records'], 0)
            assert_equal(monthly_stats.stats[u'1/2020'][u'collections'][u'download_events'], 0)

    def test_add_all_complex_filter_mixed(self):
        date = datetime(2019, 6, 1)
        resource_counts = {
            u'resource1': 10,
            u'cresource2': 51,
            u'resource2': 19,
        }
        with self.patch_collection_resources(u'cresource2 resource2'):
            monthly_stats = MonthlyStats(month=6, year=2019, resource_id=u'resource2')
            monthly_stats.add_all(date, resource_counts)
            assert_equal(monthly_stats.stats[u'6/2019'][u'research'][u'records'], 0)
            assert_equal(monthly_stats.stats[u'6/2019'][u'research'][u'download_events'], 0)
            assert_equal(monthly_stats.stats[u'6/2019'][u'collections'][u'records'], 19)
            assert_equal(monthly_stats.stats[u'6/2019'][u'collections'][u'download_events'], 1)

    def test_month_year_format(self):
        # currently the month/year keys are not zero padded so we might as well test that that is
        # still the case in case a developer gets refactor happy and changes it (I did this so maybe
        # this test is for me...)
        monthly_stats = MonthlyStats()
        for month in range(1, 12):
            date = datetime(2017, month, 1)
            monthly_stats.add_all(date, resource_counts=dict(resource1=10))
            month_year = u'{}/2017'.format(month)
            assert_equal(monthly_stats.stats[month_year][u'research'][u'records'], 10)
            assert_equal(monthly_stats.stats[month_year][u'research'][u'download_events'], 1)

    def test_add(self):
        # check that add just calls add_all
        monthly_stats = MonthlyStats()
        monthly_stats.add_all = MagicMock()
        date = MagicMock()
        resource_id = MagicMock()
        count = MagicMock()
        monthly_stats.add(date, resource_id, count)
        assert_true(monthly_stats.add_all.called)
        assert_equal(monthly_stats.add_all.call_args, call(date, {resource_id: count}))

    def test_as_dict(self):
        monthly_stats = MonthlyStats()
        monthly_stats.add(datetime(2017, 4, 1), u'resource1', 29)
        monthly_stats.add(datetime(2017, 4, 20), u'resource1', 39)
        monthly_stats.add(datetime(2013, 6, 18), u'resource2', 1000)
        monthly_stats.add(datetime(2013, 1, 8), u'resource5', 55)
        monthly_stats.add(datetime(2013, 11, 4), u'resource2', 1000)
        monthly_stats.add(datetime(2020, 10, 10), u'resource4', 92)

        stats = monthly_stats.as_dict()
        assert_true(isinstance(stats, OrderedDict))
        assert_equal(list(stats.keys()), [u'1/2013', u'6/2013', u'11/2013', u'4/2017', u'10/2020'])

    def test_update_from_backfill_no_previous_data(self):
        monthly_stats = MonthlyStats()
        monthly_stats.update_from_backfill(u'10', u'2018', {
            u'collections': {
                u'download_events': 102,
                u'records': 1029
            },
            u'research': {
                u'download_events': 4,
                u'records': 902832
            }
        })
        assert_equal(monthly_stats.stats[u'10/2018'][u'collections'][u'download_events'], 102)
        assert_equal(monthly_stats.stats[u'10/2018'][u'collections'][u'records'], 1029)
        assert_equal(monthly_stats.stats[u'10/2018'][u'research'][u'download_events'], 4)
        assert_equal(monthly_stats.stats[u'10/2018'][u'research'][u'records'], 902832)

    def test_update_from_backfill_with_previous_data(self):
        with self.patch_collection_resources(u'resource1'):
            monthly_stats = MonthlyStats()
            # this is a collection resource
            monthly_stats.add(datetime(2018, 10, 1), u'resource1', 20)
            # this isn't a collection resource
            monthly_stats.add(datetime(2018, 10, 1), u'resource2', 15)
            # update from the backfill
            monthly_stats.update_from_backfill(u'10', u'2018', {
                u'collections': {
                    u'download_events': 3,
                    u'records': 10004,
                },
                u'research': {
                    u'download_events': 5829,
                    u'records': 32894932,
                }
            })
            assert_equal(monthly_stats.stats[u'10/2018'][u'collections'][u'download_events'], 3 + 1)
            assert_equal(monthly_stats.stats[u'10/2018'][u'collections'][u'records'], 10004 + 20)
            assert_equal(monthly_stats.stats[u'10/2018'][u'research'][u'download_events'], 5829 + 1)
            assert_equal(monthly_stats.stats[u'10/2018'][u'research'][u'records'], 32894932 + 15)

    def test_update_from_backfill_with_filters(self):
        monthly_stats = MonthlyStats(month=10, year=2018)
        monthly_stats.update_from_backfill(u'10', u'2018', {
            u'collections': {
                u'download_events': 3,
                u'records': 10004,
            },
            u'research': {
                u'download_events': 5829,
                u'records': 32894932,
            }
        })
        monthly_stats.update_from_backfill(u'11', u'2018', {
            u'collections': {
                u'download_events': 3,
                u'records': 10004,
            },
            u'research': {
                u'download_events': 5829,
                u'records': 32894932,
            }
        })
        monthly_stats.update_from_backfill(u'11', u'2017', {
            u'collections': {
                u'download_events': 3,
                u'records': 10004,
            },
            u'research': {
                u'download_events': 5829,
                u'records': 32894932,
            }
        })
        assert_true(u'10/2018' in monthly_stats.stats)
        assert_true(u'11/2018' not in monthly_stats.stats)
        assert_true(u'11/2017' not in monthly_stats.stats)

    def test_update_from_gbif(self):
        monthly_stats = MonthlyStats()
        monthly_stats.update_from_gbif(10, 2018, 83, 4)
        monthly_stats.update_from_gbif(10, 2018, 18, 5)
        assert_equal(monthly_stats.stats[u'10/2018'][u'gbif'][u'download_events'], 4 + 5)
        assert_equal(monthly_stats.stats[u'10/2018'][u'gbif'][u'records'], 83 + 18)

    def test_update_from_gbif_with_filters(self):
        monthly_stats = MonthlyStats(month=10, year=2018)
        monthly_stats.update_from_gbif(10, 2019, 2389, 223)
        monthly_stats.update_from_gbif(4, 2012, 100, 28)
        monthly_stats.update_from_gbif(10, 2018, 8344, 40)
        monthly_stats.update_from_gbif(10, 2018, 40, 1)
        assert_equal(monthly_stats.stats[u'10/2018'][u'gbif'][u'download_events'], 40 + 1)
        assert_equal(monthly_stats.stats[u'10/2018'][u'gbif'][u'records'], 8344 + 40)
        assert_true(u'10/2019' not in monthly_stats.stats)
        assert_true(u'4/2012' not in monthly_stats.stats)


class TestDownloadStatistics(TestBase):
    plugins = [u'statistics', u'versioned_datastore', u'ckanpackager']

    def test_get_statistics_no_filters_calls_the_right_functions(self):
        dl_stats = DownloadStatistics(MagicMock(), MagicMock())

        dl_stats.add_ckanpackager_stats = MagicMock()
        dl_stats.add_versioned_datastore_download_stats = MagicMock()
        dl_stats.add_backfill_stats = MagicMock()
        dl_stats.add_gbif_stats = MagicMock()

        dl_stats._get_statistics()

        assert_equal(dl_stats.add_ckanpackager_stats.call_count, 1)
        assert_equal(dl_stats.add_versioned_datastore_download_stats.call_count, 1)
        assert_equal(dl_stats.add_backfill_stats.call_count, 1)
        assert_equal(dl_stats.add_gbif_stats.call_count, 1)

    def test_get_statistics_with_filters_calls_the_right_functions(self):
        dl_stats = DownloadStatistics(MagicMock(), MagicMock())

        dl_stats.add_ckanpackager_stats = MagicMock()
        dl_stats.add_versioned_datastore_download_stats = MagicMock()
        dl_stats.add_backfill_stats = MagicMock()
        dl_stats.add_gbif_stats = MagicMock()

        dl_stats._get_statistics(resource_id=MagicMock())

        assert_equal(dl_stats.add_ckanpackager_stats.call_count, 1)
        assert_equal(dl_stats.add_versioned_datastore_download_stats.call_count, 1)
        # shouldn't call these ones cause they can't be filtered by resource id
        assert_equal(dl_stats.add_backfill_stats.call_count, 0)
        assert_equal(dl_stats.add_gbif_stats.call_count, 0)

    def test_add_gbif_stats(self):
        downloads = [
            GBIFDownload(doi=u'doi1', date=datetime(2019, 8, 22), count=18),
            GBIFDownload(doi=u'doi2', date=datetime(2019, 8, 17), count=3),
            GBIFDownload(doi=u'doi3', date=datetime(2018, 8, 30), count=15),
            GBIFDownload(doi=u'doi4', date=datetime(2018, 8, 21), count=289),
            GBIFDownload(doi=u'doi5', date=datetime(2019, 2, 11), count=490),
            GBIFDownload(doi=u'doi6', date=datetime(2019, 2, 5), count=1),
            GBIFDownload(doi=u'doi7', date=datetime(2013, 1, 1), count=29000)
        ]
        for download in downloads:
            download.save()

        dl_stats = DownloadStatistics(MagicMock(), MagicMock())
        monthly_stats = MagicMock()
        dl_stats.add_gbif_stats(monthly_stats)

        calls = monthly_stats.update_from_gbif.call_args_list
        assert_equal(len(calls), 4)
        assert_true(call(1, 2013, 29000, 1) in calls)
        assert_true(call(8, 2018, 15 + 289, 2) in calls)
        assert_true(call(2, 2019, 490 + 1, 2) in calls)
        assert_true(call(8, 2019, 18 + 3, 2) in calls)

    def test_add_ckanpackager_stats(self):
        downloads = [
            CKANPackagerStat(inserted_on=datetime(2018, 4, 1), resource_id=u'resource1', count=389),
            CKANPackagerStat(inserted_on=datetime(2019, 1, 1), resource_id=u'resource2', count=910),
            CKANPackagerStat(inserted_on=datetime(2011, 12, 1), resource_id=u'resource3', count=86),
            CKANPackagerStat(inserted_on=datetime(2011, 12, 1), resource_id=u'blarp', count=None),
        ]
        for download in downloads:
            download.save()

        dl_stats = DownloadStatistics(MagicMock(), MagicMock())
        monthly_stats = MagicMock()
        dl_stats.add_ckanpackager_stats(monthly_stats)

        calls = monthly_stats.add.call_args_list
        assert_equal(len(calls), 4)
        assert_true(call(datetime(2018, 4, 1), u'resource1', 389) in calls)
        assert_true(call(datetime(2019, 1, 1), u'resource2', 910) in calls)
        assert_true(call(datetime(2011, 12, 1), u'resource3', 86) in calls)
        # the None count should be converted to 0
        assert_true(call(datetime(2011, 12, 1), u'blarp', 0) in calls)

    def add_versioned_datastore_download_stats(self):
        default_kwargs = {
            u'query_hash': u'abcd',
            u'query': {},
            u'query_version': u'v12.4.9',
            u'resource_ids_and_versions': {},
            u'total': 1,
            u'options': {},
        }
        downloads = [
            DatastoreDownload(resource_totals={u'resource1': 100, u'resource2': 32},
                              created=datetime(2019, 1, 1), state=state_complete, error=None,
                              **default_kwargs),
            DatastoreDownload(resource_totals={u'resource1': 100, u'resource2': 32},
                              created=datetime(2019, 3, 30), state=state_complete, error=None,
                              **default_kwargs),
            DatastoreDownload(resource_totals={u'resource1': 4}, created=datetime(2018, 5, 10),
                              state=state_complete, error=u'error!', **default_kwargs),
            DatastoreDownload(resource_totals={u'resource3': 189}, created=datetime(2018, 4, 14),
                              state=state_zipping, error=None, **default_kwargs),
        ]
        for download in downloads:
            download.save()

        dl_stats = DownloadStatistics(MagicMock(), MagicMock())
        monthly_stats = MagicMock()
        dl_stats.add_versioned_datastore_download_stats(monthly_stats)

        calls = monthly_stats.add.call_args_list
        assert_equal(len(calls), 2)
        # only these two should come through, the others are either in error or not complete
        assert_true(call(datetime(2019, 1, 1), {u'resource1': 100, u'resource2': 32}) in calls)
        assert_true(call(datetime(2019, 3, 30), {u'resource1': 100, u'resource2': 32}) in calls)
