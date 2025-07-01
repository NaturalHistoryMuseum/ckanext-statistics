import itertools

import ckantools.config
import requests
from beaker.cache import cache_region

gbif_api_url = 'https://api.gbif.org/v1/occurrence/download/statistics'


@cache_region('ckanext_statistics', 'gbif_stats')
def get_gbif_stats(year=None, month=None):
    """
    Retrieve download statistics from GBIF's API.

    :param year: optional year to filter results by
    :param month: optional month to filter results by
    :returns: total records downloaded and total download events across the time frame
        (or all time)
    :rtype: dict
    """
    dataset_keys = ckantools.config.get_setting(
        'ckanext.statistics.gbif_dataset_keys', 'ckanext.gbif.dataset_key', default=''
    )
    dataset_keys = set(dataset_keys.split(' '))

    all_results = []

    for dataset_key in dataset_keys:
        params = {'datasetKey': dataset_key, 'limit': 20, 'offset': 0}
        if year and month:
            params['fromDate'] = f'{year}-{month}'
            params['toDate'] = f'{year}-{month}'
        elif year:
            params['fromDate'] = f'{year}-01'
            params['toDate'] = f'{year}-12'

        while True:
            r = requests.get(gbif_api_url, params=params)
            if not r.ok:
                break
            response_json = r.json()
            page_results = response_json.get('results', [])
            for r in page_results:
                if month and r['month'] != month:
                    continue
                all_results.append(
                    {
                        'year': r['year'],
                        'month': r['month'],
                        'records': r['totalRecords'],
                        'events': r['numberDownloads'],
                    }
                )

            if response_json.get('endOfRecords', True) or len(page_results) == 0:
                break
            params['offset'] += 20

    def _compress_results(key, results):
        results = list(results)
        return {
            'year': key[0],
            'month': key[1],
            'records': sum(r['records'] for r in results),
            'events': sum(r['events'] for r in results),
        }

    grouped_results = [
        _compress_results(k, v)
        for k, v in itertools.groupby(
            sorted(all_results, key=lambda x: (x['year'], x['month'])),
            key=lambda x: (x['year'], x['month']),
        )
    ]

    return grouped_results
