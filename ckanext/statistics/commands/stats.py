import re
import os
import requests
import pylons
import logging
import ckan.model as model

import ckan.logic as logic
from ckan.plugins import toolkit
from ckan.lib.cli import CkanCommand

from ckanext.statistics.model import Base
from ckanext.statistics.model.gbif_download import GBIFDownload
from ckanext.statistics.model.datastore import DatastoreStat

log = logging.getLogger()


class StatsCommand(CkanCommand):
    """
    Create stats from GBIF

    paster stats gbif -c /etc/ckan/default/development.ini

    """

    summary = __doc__.split('\n')[0]
    usage = __doc__

    def command(self):
        self._load_config()
        # Create the table if it doesn't exist
        self._create_table()

        cmd = self.args[0]

        if cmd == 'gbif':
            self.gbif_stats()
        elif cmd == 'datastore':
            self.datastore_stats()
        model.Session.commit()

    @staticmethod
    def _create_table():
        Base.metadata.create_all(model.meta.engine)

    @staticmethod
    def gbif_stats():
        last_download = model.Session.query(GBIFDownload).order_by(GBIFDownload.date.desc()).first()

        dataset_uuid = pylons.config['ckanext.gbif.dataset_key']

        offset = 0
        limit = 100

        while True:
            print 'Retrieving page offset %s' % offset

            # Now GBIF is using angular, we can hit their json endpoint directly
            url = os.path.join('http://api.gbif.org/v1/occurrence/download/dataset', dataset_uuid)
            r = requests.get(url, params={'offset': offset, 'limit': limit})
            response = r.json()
            if not response['results']:
                return

            for record in response['results']:
                # If the record has the same DOI as the last download, stop processing

                if last_download and last_download.doi == record['download']['doi']:
                    return

                # Create new download object
                download = GBIFDownload(
                    count=record['numberRecords'],
                    doi=record['download']['doi'],
                    date=record['download']['created'],
                )
                model.Session.add(download)

            offset += limit

    @staticmethod
    def datastore_stats():

        context = {'user': 'admin'}

        # # Get any SOLR datasets
        # k = 'ckanext.datasolr.'
        # solr_datasets = [c.replace(k, '') for c in pylons.config.keys() if k in c]
        pkgs = toolkit.get_action('current_package_list_with_resources')(context, {'limit': 200})
        for pkg_dict in pkgs:
            if pkg_dict['private']:
                continue

            if 'resources' in pkg_dict:
                for resource in pkg_dict['resources']:
                    # Does this have an activate datastore table?
                    if resource['url_type'] in ['datastore', 'upload', 'dataset']:
                        data = {
                            'resource_id': resource['id'],
                            'limit': 1
                        }
                        try:
                            search = toolkit.get_action('datastore_search')({}, data)
                        except logic.NotFound:
                            # Not every file is uploaded to the datastore, so ignore it
                            continue

                        count = search.get('total')

                        # Get latest record for this dataset
                        latest_count = model.Session.query(DatastoreStat).filter(DatastoreStat.resource_id==resource['id']).order_by(DatastoreStat.date.desc()).first()

                        # If count hasn't changed, don't update it
                        if latest_count and latest_count.count == count:
                            continue

                        stats = DatastoreStat(count=count, resource_id=resource['id'], date=d)
                        model.Session.add(stats)
