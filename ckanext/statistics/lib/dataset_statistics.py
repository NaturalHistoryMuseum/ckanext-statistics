#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK

from solr import SolrException
import ckan.logic as logic
from ckan.common import c, _
import ckan.model as model
import logging
import ckan.plugins as p
import ckan.lib.base as base

from ckanext.statistics.lib.statistics import Statistics
from ckanext.statistics.logic.schema import statistics_dataset_schema

_check_access = logic.check_access
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
get_action = logic.get_action

render = base.render
abort = base.abort
redirect = base.redirect

log = logging.getLogger(__name__)


class DatasetStatistics(Statistics):
    '''
        Retrieve dataset statistics
    '''

    schema = statistics_dataset_schema()

    def _get_statistics(self, resource_id=None):
        '''
        Fetch the statistics
        '''
        context = {u'model': model, u'user': c.user or c.author, u'auth_user_obj': c.userobj}
        if resource_id:
            return self._get_resource_statistics(resource_id, context)
        else:
            return self._get_all_resources_statistics(context)

    @staticmethod
    def _get_all_resources_statistics(context):

        stats = {
            u'total': 0,
            u'resources': []
        }

        pkgs = p.toolkit.get_action(u'current_package_list_with_resources')(context, {u'limit': 200})
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
                            search = p.toolkit.get_action(u'datastore_search')({}, data)
                        except (logic.NotFound, SolrException):
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

    def _get_resource_statistics(self, resource_id, context):
        '''
        Get stats for an individual resource
        @param resource_id:
        @return:
        '''
        try:
            resource = get_action(u'resource_show')(self.context, {u'id': resource_id})
        except NotFound:
            abort(404, _(u'Resource not found'))
        except NotAuthorized:
            abort(401, _(u'Unauthorized to read resource %s') % resource_id)
        else:

            # TODO - Add break down over time for SOLR Datasets
            # k = 'ckanext.datasolr.'
            # solr_datasets = [c.replace(k, '') for c in pylons.config.keys() if k in c]
            # facet.date=created&facet.date.start=2010-01-01T00:00:00.000Z&facet.date.end=NOW&facet.date.gap=%2B1MONTH
            search = p.toolkit.get_action(u'datastore_search')({}, {u'resource_id': resource_id, u'limit': 1})

            return {
                u'resource': resource,
                u'total': search[u'total']
            }
