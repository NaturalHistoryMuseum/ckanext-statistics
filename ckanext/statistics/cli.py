import click
import requests
from ckan import model
from ckan.plugins import toolkit
from tqdm import tqdm

from .model.gbif_download import gbif_downloads_table, GBIFDownload


def get_commands():
    return [statistics]


@click.group()
def statistics():
    pass


@statistics.command(name='initdb')
def init_db():
    """
    Initialises the gbif_downloads table if it doesn't exist.
    """
    if not gbif_downloads_table.exists():
        gbif_downloads_table.create()
        click.secho('Created gbif_downloads table', fg='green')
    else:
        click.secho('Table gbif_downloads already exists', fg='green')


@statistics.command(name='update-gbif-stats')
def update_gbif_stats():
    """
    Get download stats for the specimen dataset from GBIF's API.
    """
    # make sure the table we need exists first
    if not gbif_downloads_table.exists():
        gbif_downloads_table.create()
        click.secho('Created gbif_downloads table', fg='green')

    last_download = (
        model.Session.query(GBIFDownload).order_by(GBIFDownload.date.desc()).first()
    )
    seen_dois = set()
    dataset_uuid = toolkit.config['ckanext.gbif.dataset_key']
    count = 0

    for record in tqdm(get_gbif_stats(dataset_uuid), unit='record'):
        doi = record['download']['doi']

        # if the record has the same DOI as the last download, stop processing
        if last_download and last_download.doi == doi:
            break

        # if we've seen the doi before in this run, skip it - we need to do this because the
        # gbif api's return is in reverse chronological order so the first record we receive
        # is the latest download. This is an issue when iterating over the data as we could,
        # if new downloads occur between page requests, receive data about a download twice.
        if doi in seen_dois:
            continue
        else:
            seen_dois.add(doi)

        # create new download object
        download = GBIFDownload(
            doi=doi,
            count=record['numberRecords'],
            date=record['download']['created'],
        )
        download.save()
        count += 1

    click.secho(f'Finished updating stats with {count} new downloads', fg='green')


def get_gbif_stats(dataset_uuid, limit=100):
    """
    Generates download statistic records from the GBIF API for the given dataset_uuid.

    :param dataset_uuid: the dataset uuid to get stats records for
    :param limit: the number of records to retrieve at once (default: 100)
    :return: yields dicts
    """
    offset = 0
    url = f'https://api.gbif.org/v1/occurrence/download/dataset/{dataset_uuid}'

    while True:
        r = requests.get(url, params=dict(offset=offset, limit=limit))
        r.raise_for_status()
        response = r.json()

        if not response['results']:
            return

        for record in response['results']:
            yield record

        offset += limit
