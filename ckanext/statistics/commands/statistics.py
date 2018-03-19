# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK

import logging

import os
import requests
from ckanext.statistics.model import Base
from ckanext.statistics.model.gbif_download import GBIFDownload

import ckan.model as model
from ckan.plugins import toolkit

log = logging.getLogger()


class StatisticsCommand(toolkit.CkanCommand):
    '''Create stats from GBIF
    
    paster --plugin=ckanext-statistics statistics gbif -c /etc/ckan/default/development.ini

    '''

    summary = __doc__.split(u'\n')[0]
    usage = __doc__

    def command(self):
        '''Run the command and retrieve the statistics.'''
        self._load_config()
        # Create the table if it doesn't exist
        self._create_table()

        cmd = self.args[0]

        if cmd == u'gbif':
            self.get_gbif_stats()

        model.Session.commit()

    @staticmethod
    def _create_table():
        Base.metadata.create_all(model.meta.engine)

    @staticmethod
    def get_gbif_stats():
        '''Get stats from GBIF's API.'''
        last_download = model.Session.query(GBIFDownload).order_by(
            GBIFDownload.date.desc()).first()

        dataset_uuid = toolkit.config[u'ckanext.gbif.dataset_key']

        offset = 0
        limit = 100

        while True:
            print u'Retrieving page offset %s' % offset

            # Now GBIF is using angular, we can hit their json endpoint directly
            url = os.path.join(u'http://api.gbif.org/v1/occurrence/download/dataset',
                               dataset_uuid)
            r = requests.get(url, params={
                u'offset': offset,
                u'limit': limit
                })
            response = r.json()
            if not response[u'results']:
                return

            for record in response[u'results']:
                # If the record has the same DOI as the last download, stop processing

                if last_download and last_download.doi == record[u'download'][u'doi']:
                    return

                # Create new download object
                download = GBIFDownload(
                    count=record[u'numberRecords'],
                    doi=record[u'download'][u'doi'],
                    date=record[u'download'][u'created'],
                    )
                model.Session.merge(download)
                model.Session.commit()

            offset += limit
