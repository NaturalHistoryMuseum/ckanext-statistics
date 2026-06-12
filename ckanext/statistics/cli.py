import click
from ckantools.cache import CacheClearError, clear_cache_region

from ckanext.statistics.lib import dataset_statistics, download_statistics, gbif_api


def get_commands():
    return [statistics]


@click.group()
def statistics():
    """
    Perform various tasks on the versioned datastore.
    """
    pass


@statistics.command()
def clear_cache():
    try:
        clear_cache_region(
            'statistics', download_statistics, cache_name='statistics_long'
        )
        clear_cache_region(
            'statistics', dataset_statistics, gbif_api, cache_name='statistics_short'
        )
        click.secho('Cleared statistics cache', fg='green')
    except CacheClearError as e:
        click.secho(f'Failed to clear statistics cache: {e}', fg='red')
