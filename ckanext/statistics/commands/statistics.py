import re
import os
import requests
import pylons
import logging
import ckan.model as model

from ckan.lib.cli import CkanCommand

from ckanext.statistics.model import Base
from ckanext.statistics.model.gbif_download import GBIFDownload

log = logging.getLogger()


class StatisticsCommand(CkanCommand):
    """
    Create stats from GBIF

    paster --plugin=ckanext-statistics statistics gbif -c /etc/ckan/default/development.ini

    """

    summary = __doc__.split('\n')[0]
    usage = __doc__

    def command(self):
        self._load_config()
        # Create the table if it doesn't exist
        self._create_table()

        cmd = self.args[0]

        if cmd == 'gbif':
            self.get_gbif_stats()

        model.Session.commit()

    @staticmethod
    def _create_table():
        Base.metadata.create_all(model.meta.engine)

    @staticmethod
    def get_gbif_stats():
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
                model.Session.merge(download)
                model.Session.commit()

            offset += limit
