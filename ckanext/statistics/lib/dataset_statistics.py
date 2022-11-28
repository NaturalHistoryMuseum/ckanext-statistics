# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


import logging
from ckan.lib.search import SearchIndexError
from ckan.plugins import toolkit

from ckanext.statistics.lib.statistics import Statistics
from ckanext.statistics.logic.schema import statistics_dataset_schema

log = logging.getLogger(__name__)


class DatasetStatistics(Statistics):
    """
    Retrieve dataset statistics.
    """

    schema = statistics_dataset_schema()

    def _get_statistics(self, resource_id=None):
        """
        Fetch the statistics.

        :param resource_id: a resource ID if the stats for only one resource is required
                            - None retrieves stats for all resources
                            (optional, default: None)
        """
        context = {
            'user': toolkit.c.user or toolkit.c.author,
            'auth_user_obj': toolkit.c.userobj,
        }
        if resource_id:
            return self._get_resource_statistics(resource_id)
        else:
            return self._get_all_resources_statistics(context)

    @staticmethod
    def _get_all_resources_statistics(context):
        """
        Get stats for all resources.

        :param context: the current context
        """
        total = 0
        resources = []
        package_data_dict = {'limit': 50, 'offset': 0}

        while True:
            packages = toolkit.get_action('current_package_list_with_resources')(
                context, package_data_dict
            )
            if not packages:
                # we've hit all the packages that are available
                break
            else:
                package_data_dict['offset'] += len(packages)

                for package in packages:
                    # only include resources from packages that are public and active
                    if package['private'] or package['state'] != 'active':
                        continue
                    for resource in package.get('resources', []):
                        if resource['state'] != 'active':
                            continue
                        if resource.get('datastore_active', False):
                            try:
                                search = toolkit.get_action('datastore_search')(
                                    {}, {'resource_id': resource['id'], 'limit': 0}
                                )
                            except (toolkit.ObjectNotFound, SearchIndexError):
                                # not every file is ingested into the datastore, ignore these errors
                                continue

                            resources.append(
                                {
                                    'pkg_name': package['name'],
                                    'pkg_title': package['title'],
                                    'name': resource['name'],
                                    'id': resource['id'],
                                    'total': search.get('total', 0),
                                }
                            )
                            total += search.get('total', 0)

        return {'total': total, 'resources': resources}

    def _get_resource_statistics(self, resource_id):
        """
        Get stats for an individual resource.

        :param resource_id: the ID of the resource to retrieve stats for
        """
        try:
            resource = toolkit.get_action('resource_show')(
                self.context, {'id': resource_id}
            )
        except toolkit.ObjectNotFound:
            toolkit.abort(404, toolkit._('Resource not found'))
        except toolkit.NotAuthorized:
            toolkit.abort(
                401, toolkit._(f'Unauthorized to read resource {resource_id}')
            )
        else:
            # TODO - Add break down over time for SOLR Datasets
            search = toolkit.get_action('datastore_search')(
                {}, {'resource_id': resource_id, 'limit': 1}
            )

            return {'resource': resource, 'total': search['total']}
