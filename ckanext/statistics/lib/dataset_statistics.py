# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


import logging

from ckanext.statistics.lib.statistics import Statistics
from ckanext.statistics.logic.schema import statistics_dataset_schema

from ckan.lib.search import SearchIndexError
from ckan.plugins import toolkit

log = logging.getLogger(__name__)


class DatasetStatistics(Statistics):
    '''Retrieve dataset statistics'''

    schema = statistics_dataset_schema()

    def _get_statistics(self, resource_id=None):
        '''Fetch the statistics.

        :param resource_id: a resource ID if the stats for only one resource is required
                            - None retrieves stats for all resources
                            (optional, default: None)

        '''
        context = {
            u'user': toolkit.c.user or toolkit.c.author,
            u'auth_user_obj': toolkit.c.userobj
            }
        if resource_id:
            return self._get_resource_statistics(resource_id)
        else:
            return self._get_all_resources_statistics(context)

    @staticmethod
    def _get_all_resources_statistics(context):
        '''Get stats for all resources.

        :param context: the current context

        '''

        stats = {
            u'total': 0,
            u'resources': []
            }

        pkgs = toolkit.get_action(u'current_package_list_with_resources')(context, {
            u'limit': 200
            })
        for pkg_dict in pkgs:
            if pkg_dict[u'private'] or pkg_dict[u'state'] != u'active':
                continue

            if u'resources' in pkg_dict:
                for resource in pkg_dict[u'resources']:
                    if resource[u'state'] != u'active':
                        continue
                    # Does this have an activate datastore table?
                    if resource[u'url_type'] in [u'datastore', u'upload', u'dataset']:
                        data = {
                            u'resource_id': resource[u'id'],
                            u'limit': 1
                            }
                        try:
                            search = toolkit.get_action('datastore_search')({}, data)
                        except (toolkit.ObjectNotFound, SearchIndexError):
                            # Not every file is uploaded to the datastore, so ignore it
                            continue

                        stats[u'resources'].append(
                            {
                                u'pkg_name': pkg_dict[u'name'],
                                u'pkg_title': pkg_dict[u'title'],
                                u'name': resource[u'name'],
                                u'id': resource[u'id'],
                                u'total': search.get(u'total', 0)
                                }
                            )
                        stats[u'total'] += search.get(u'total', 0)
        return stats

    def _get_resource_statistics(self, resource_id):
        '''Get stats for an individual resource

        :param resource_id: the ID of the resource to retrieve stats for

        '''
        try:
            resource = toolkit.get_action(u'resource_show')(self.context, {
                u'id': resource_id
                })
        except toolkit.ObjectNotFound:
            toolkit.abort(404, toolkit._(u'Resource not found'))
        except toolkit.NotAuthorized:
            toolkit.abort(401,
                          toolkit._(u'Unauthorized to read resource %s') % resource_id)
        else:

            # TODO - Add break down over time for SOLR Datasets
            search = toolkit.get_action(u'datastore_search')({}, {
                u'resource_id': resource_id,
                u'limit': 1
                })

            return {
                u'resource': resource,
                u'total': search[u'total']
                }
