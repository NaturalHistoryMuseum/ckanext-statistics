from unittest.mock import patch

import pytest

from ckanext.statistics.lib.gbif_api import get_gbif_stats


@pytest.mark.ckan_config('ckan.plugins', 'statistics')
@pytest.mark.ckan_config('ckanext.statistics.cache.expire', 0)
@pytest.mark.usefixtures('with_plugins')
class TestGbifStats(object):
    @pytest.mark.ckan_config('ckanext.statistics.gbif_dataset_keys', 'abcd')
    @patch('ckanext.statistics.lib.gbif_api.requests.get')
    def test_get_gbif_stats(self, mock_get):
        mock_get.return_value.json.return_value = {
            'offset': 0,
            'limit': 20,
            'endOfRecords': True,
            'count': 3,
            'results': [
                {
                    'datasetKey': 'abcd',
                    'totalRecords': 3000,
                    'numberDownloads': 15,
                    'year': 2025,
                    'month': 3,
                },
                {
                    'datasetKey': 'abcd',
                    'totalRecords': 2000,
                    'numberDownloads': 10,
                    'year': 2020,
                    'month': 2,
                },
                {
                    'datasetKey': 'abcd',
                    'totalRecords': 1000,
                    'numberDownloads': 5,
                    'year': 2015,
                    'month': 1,
                },
            ],
        }
        results = get_gbif_stats()
        assert mock_get.call_count == 1
        assert len(results) == 3

        records_2015 = [r for r in results if r['year'] == 2015]
        assert len(records_2015) == 1
        assert records_2015[0]['month'] == 1
        assert records_2015[0]['records'] == 1000
        assert records_2015[0]['events'] == 5

    @pytest.mark.ckan_config('ckanext.statistics.gbif_dataset_keys', 'abcd')
    @patch('ckanext.statistics.lib.gbif_api.requests.get')
    def test_get_gbif_stats_with_year(self, mock_get):
        # not much point in testing the processing of dummy data again so we'll just
        # test that the parameters got passed correctly
        mock_get.return_value.json.return_value = {
            'offset': 0,
            'limit': 20,
            'endOfRecords': True,
            'count': 0,
            'results': [],
        }

        get_gbif_stats(year=2025)
        assert mock_get.call_count == 1
        assert mock_get.call_args.kwargs['params']['fromDate'] == '2025-01'
        assert mock_get.call_args.kwargs['params']['toDate'] == '2025-12'

    @pytest.mark.ckan_config('ckanext.statistics.gbif_dataset_keys', 'abcd')
    @patch('ckanext.statistics.lib.gbif_api.requests.get')
    def test_get_gbif_stats_with_month(self, mock_get):
        mock_get.return_value.json.return_value = {
            'offset': 0,
            'limit': 20,
            'endOfRecords': True,
            'count': 3,
            'results': [
                {
                    'datasetKey': 'abcd',
                    'totalRecords': 3000,
                    'numberDownloads': 15,
                    'year': 2025,
                    'month': 3,
                },
                {
                    'datasetKey': 'abcd',
                    'totalRecords': 2000,
                    'numberDownloads': 10,
                    'year': 2020,
                    'month': 2,
                },
                {
                    'datasetKey': 'abcd',
                    'totalRecords': 1000,
                    'numberDownloads': 5,
                    'year': 2015,
                    'month': 3,
                },
            ],
        }
        results = get_gbif_stats(month=3)
        assert mock_get.call_count == 1
        assert 'fromDate' not in mock_get.call_args.kwargs['params']
        assert 'toDate' not in mock_get.call_args.kwargs['params']
        assert len(results) == 2

        for r in results:
            assert r['month'] == 3

    @pytest.mark.ckan_config('ckanext.statistics.gbif_dataset_keys', 'abcd')
    @patch('ckanext.statistics.lib.gbif_api.requests.get')
    def test_get_gbif_stats_with_year_and_month(self, mock_get):
        # not much point in testing the processing of dummy data again so we'll just
        # test that the parameters got passed correctly
        mock_get.return_value.json.return_value = {
            'offset': 0,
            'limit': 20,
            'endOfRecords': True,
            'count': 0,
            'results': [],
        }

        get_gbif_stats(year=2025, month=5)
        assert mock_get.call_count == 1
        assert mock_get.call_args.kwargs['params']['fromDate'] == '2025-05'
        assert mock_get.call_args.kwargs['params']['toDate'] == '2025-05'

    @pytest.mark.ckan_config('ckanext.statistics.gbif_dataset_keys', 'abcd efgh')
    @patch('ckanext.statistics.lib.gbif_api.requests.get')
    def test_get_gbif_stats_multiple_keys(self, mock_get):
        mock_get.return_value.json.return_value = {
            'offset': 0,
            'limit': 20,
            'endOfRecords': True,
            'count': 3,
            'results': [
                {
                    'datasetKey': 'abcdefgh',
                    'totalRecords': 0,
                    'numberDownloads': 0,
                    'year': 2025,
                    'month': 3,
                },
                {
                    'datasetKey': 'abcdefgh',
                    'totalRecords': 0,
                    'numberDownloads': 0,
                    'year': 2020,
                    'month': 2,
                },
                {
                    'datasetKey': 'abcdefgh',
                    'totalRecords': 1000,
                    'numberDownloads': 5,
                    'year': 2015,
                    'month': 1,
                },
            ],
        }
        results = get_gbif_stats()
        assert mock_get.call_count == 2
        assert len(results) == 3

        records_2015 = [r for r in results if r['year'] == 2015]
        assert len(records_2015) == 1
        assert records_2015[0]['month'] == 1
        assert records_2015[0]['records'] == 2000
        assert records_2015[0]['events'] == 10
