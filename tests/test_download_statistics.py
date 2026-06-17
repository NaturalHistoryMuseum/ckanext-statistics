# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from ckanext.statistics.lib.download_statistics import DownloadStatistics
from ckanext.statistics.model.ckanpackager import (
    CKANPackagerStat,
    ckanpackager_stats_table,
)
from ckanext.versioned_datastore.model import details, downloads, slugs, stats
from ckanext.versioned_datastore.model.downloads import (
    CoreFileRecord,
    DownloadRequest,
)


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
        slugs.navigational_slugs_table,
        details.datastore_resource_details_table,
        downloads.datastore_downloads_core_files_table,
        downloads.datastore_downloads_derivative_files_table,
        downloads.datastore_downloads_requests_table,
        ckanpackager_stats_table,
    ]
    # create the tables if they don't exist
    for table in tables:
        if not table.exists():
            table.create()


@pytest.mark.ckan_config('ckan.plugins', 'statistics versioned_datastore')
@pytest.mark.usefixtures('with_needed_tables', 'with_plugins')
@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
class TestDownloadStatistics(object):
    def test_get_statistics_no_filters_calls_the_right_functions(self):
        dl_stats = DownloadStatistics(MagicMock())

        dl_stats._get_ckanpackager = MagicMock()
        dl_stats._get_ckanpackager.return_value = {}
        dl_stats._get_vds_download = MagicMock()
        dl_stats._get_vds_download.return_value = {}
        dl_stats._get_gbif = MagicMock()
        dl_stats._get_gbif.return_value = {}
        dl_stats._get_backfill = MagicMock()
        dl_stats._get_backfill.return_value = {}
        dl_stats._get_empties = MagicMock()
        dl_stats._get_empties.return_value = {}

        dl_stats.get()

        # called twice to refresh current month
        assert dl_stats._get_ckanpackager.call_count == 2
        assert dl_stats._get_vds_download.call_count == 2
        assert dl_stats._get_gbif.call_count == 2
        assert dl_stats._get_backfill.call_count == 2
        # just once
        assert dl_stats._get_empties.call_count == 1

    def test_get_statistics_with_resource_id_calls_the_right_functions(self):
        dl_stats = DownloadStatistics(MagicMock())

        dl_stats._get_ckanpackager = MagicMock()
        dl_stats._get_ckanpackager.return_value = {}
        dl_stats._get_vds_download = MagicMock()
        dl_stats._get_vds_download.return_value = {}
        dl_stats._get_gbif = MagicMock()
        dl_stats._get_gbif.return_value = {}
        dl_stats._get_backfill = MagicMock()
        dl_stats._get_backfill.return_value = {}
        dl_stats._get_empties = MagicMock()
        dl_stats._get_empties.return_value = {}

        dl_stats.get(resource_id=MagicMock())

        # called twice to refresh current month
        assert dl_stats._get_ckanpackager.call_count == 2
        assert dl_stats._get_vds_download.call_count == 2
        # shouldn't call these ones because they can't be filtered by resource id
        assert dl_stats._get_gbif.call_count == 0
        assert dl_stats._get_backfill.call_count == 0
        # just once
        assert dl_stats._get_empties.call_count == 1

    def test_date_format(self):
        # currently the month/year keys are not zero padded so we might as well test
        # that that is still the case in case a developer gets refactor happy and
        # changes it
        dl_stats = DownloadStatistics(MagicMock())
        for month in range(1, 12):
            date = datetime(2017, month, 1)
            target_format = '{}/2017'.format(month)
            assert dl_stats._date_format(date) == target_format
            assert dl_stats._date_format(year=2017, month=month) == target_format

        assert dl_stats._date_format(datetime(2025, 1, 1)) == '1/2025'
        assert dl_stats._date_format(year=2026, month=2) == '2/2026'

    @pytest.mark.ckan_config('ckanext.statistics.resource_ids', 'resource1')
    def test_get_ckanpackager(self):
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

        dl_stats = DownloadStatistics(MagicMock())
        returned_stats = dl_stats._get_ckanpackager()

        assert '4/2018' in returned_stats
        assert returned_stats['4/2018']['research'] == {
            'download_events': 0,
            'records': 0,
        }, 'research wrong'
        assert returned_stats['4/2018']['collections'] == {
            'download_events': 1,
            'records': 389,
        }, 'collections wrong'
        assert '1/2019' in returned_stats
        assert returned_stats['1/2019']['research'] == {
            'download_events': 1,
            'records': 910,
        }
        assert returned_stats['1/2019']['collections'] == {
            'download_events': 0,
            'records': 0,
        }
        assert '12/2011' in returned_stats
        assert returned_stats['12/2011']['research'] == {
            'download_events': 2,
            'records': 86,
        }
        assert returned_stats['12/2011']['collections'] == {
            'download_events': 0,
            'records': 0,
        }

    @pytest.mark.ckan_config('ckanext.statistics.resource_ids', 'resource1')
    def test_get_vds_download(self):
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
            **core_record_kwargs,
        )
        core_record_1.save()

        core_record_2 = CoreFileRecord(
            resource_ids_and_versions={'resource2': 1},
            query_hash='efgh',
            resource_hash='efgh',
            modified=datetime(2018, 5, 10),
            resource_totals={'resource2': 4},
            **core_record_kwargs,
        )
        core_record_2.save()

        core_record_3 = CoreFileRecord(
            resource_ids_and_versions={'resource3': 1},
            query_hash='ijkl',
            resource_hash='ijkl',
            modified=datetime(2018, 4, 14),
            resource_totals={'resource3': 189},
            **core_record_kwargs,
        )
        core_record_3.save()

        downloads = [
            DownloadRequest(
                created=datetime(2019, 1, 1),
                state=DownloadRequest.state_complete,
                core_id=core_record_1.id,
            ),
            DownloadRequest(
                created=datetime(2019, 3, 20),
                state=DownloadRequest.state_complete,
                core_id=core_record_2.id,
            ),
            DownloadRequest(
                created=datetime(2019, 3, 30),
                state=DownloadRequest.state_complete,
                core_id=core_record_3.id,
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

        dl_stats = DownloadStatistics(MagicMock())
        returned_stats = dl_stats._get_vds_download()

        assert '1/2019' in returned_stats
        assert returned_stats['1/2019']['collections'] == {
            'download_events': 0,
            'records': 100,
        }
        assert returned_stats['1/2019']['research'] == {
            'download_events': 0,
            'records': 32,
        }
        assert returned_stats['1/2019']['mixed'] == {
            'download_events': 1,
            'records': 0,
        }
        assert '3/2019' in returned_stats
        assert returned_stats['3/2019']['research'] == {
            'download_events': 2,
            'records': 193,
        }
        # any requests without "complete" status should not be added
        assert '5/2018' not in returned_stats
        assert '4/2018' not in returned_stats

    @patch('ckanext.statistics.lib.download_statistics.get_gbif_stats')
    def test_get_gbif(self, mock_get_gbif_stats):
        mock_get_gbif_stats.return_value = [
            {'year': 2010, 'month': 1, 'records': 100, 'events': 2},
            {'year': 2015, 'month': 2, 'records': 150, 'events': 3},
            {'year': 2020, 'month': 3, 'records': 20, 'events': 2},
            {'year': 2025, 'month': 4, 'records': 29000, 'events': 15},
        ]

        dl_stats = DownloadStatistics(MagicMock())
        returned_stats = dl_stats._get_gbif()

        assert '1/2010' in returned_stats
        assert returned_stats['1/2010']['gbif'] == {
            'download_events': 2,
            'records': 100,
        }
        assert '2/2015' in returned_stats
        assert returned_stats['2/2015']['gbif'] == {
            'download_events': 3,
            'records': 150,
        }
        assert '3/2020' in returned_stats
        assert returned_stats['3/2020']['gbif'] == {
            'download_events': 2,
            'records': 20,
        }
        assert '4/2025' in returned_stats
        assert returned_stats['4/2025']['gbif'] == {
            'download_events': 15,
            'records': 29000,
        }
