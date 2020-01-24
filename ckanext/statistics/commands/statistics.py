# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK

import logging

import os
import requests
from ..model.gbif_download import gbif_downloads_table, GBIFDownload

import ckan.model as model
from ckan.plugins import toolkit

log = logging.getLogger()


class StatisticsCommand(toolkit.CkanCommand):
    '''
    Initialise gbif_downloads table and populate it from the GBIF API.

    paster --plugin=ckanext-statistics statistics initdb -c /etc/ckan/default/development.ini
    paster --plugin=ckanext-statistics statistics gbif -c /etc/ckan/default/development.ini
    '''

    summary = __doc__.split(u'\n')[0]
    usage = __doc__

    def command(self):
        '''
        Run the command and retrieve the statistics.
        '''
        self._load_config()

        cmd = self.args[0]
        if cmd == u'initdb':
            self.initdb()
        elif cmd == u'gbif':
            self.get_gbif_stats()

    def initdb(self):
        '''
        Initialises the gbif_downloads table if it doesn't exist.
        :return:
        '''
        if not gbif_downloads_table.exists(model.meta.engine):
            gbif_downloads_table.create(model.meta.engine)

    def get_gbif_stats(self):
        '''
        Get stats from GBIF's API.
        '''
        # make sure the database exists first
        self.initdb()

        last_download = model.Session.query(GBIFDownload).order_by(GBIFDownload.date.desc()).first()
        seen_dois = set()
        dataset_uuid = toolkit.config[u'ckanext.gbif.dataset_key']
        offset = 0
        limit = 100

        while True:
            print u'Retrieving page offset %s' % offset

            # use the GBIF API to get the download stats
            url = os.path.join(u'http://api.gbif.org/v1/occurrence/download/dataset', dataset_uuid)
            r = requests.get(url, params={
                u'offset': offset,
                u'limit': limit
            })
            response = r.json()
            if not response[u'results']:
                return

            for record in response[u'results']:
                doi = record[u'download'][u'doi']

                # if the record has the same DOI as the last download, stop processing
                if last_download and last_download.doi == doi:
                    return

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
                    count=record[u'numberRecords'],
                    date=record[u'download'][u'created'],
                )
                download.save()

            offset += limit
