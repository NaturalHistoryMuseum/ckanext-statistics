# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


import logging

from ckan.plugins import toolkit

from ckanext.statistics.lib.statistics import Statistics

log = logging.getLogger(__name__)


class DatasetStatistics(Statistics):
    """
    Retrieve dataset statistics.
    """

    def get(self, resource_id=None):
        """
        Fetch the statistics.

        :param resource_id: a resource ID if the stats for only one resource is required
                            - None retrieves stats for all resources
                            (optional, default: None)
        """
        if resource_id:
            return self._get_resource_statistics(resource_id)
        else:
            return self._get_all_resources_statistics()

    def _get_all_resources_statistics(self):
        """
        Get stats for all resources.
        """
        total = 0
        resources = []
        package_data_dict = {'limit': 100, 'offset': 0}

        while True:
            # only check public packages
            packages = toolkit.get_action('current_package_list_with_resources')(
                {'ignore_auth': False, 'user': None}, package_data_dict
            )
            if not packages:
                # we've hit all the packages that are available
                break
            else:
                package_data_dict['offset'] += len(packages)

                for package in packages:
                    for resource in package.get('resources', []):
                        try:
                            # only check public resources
                            resource_count = toolkit.get_action('vds_basic_count')(
                                {'ignore_auth': False, 'user': None},
                                {'resource_id': resource['id']},
                            )
                        except toolkit.ValidationError:
                            # anything that isn't a public datastore resource will error
                            continue

                        resources.append(
                            {
                                'pkg_name': package['name'],
                                'pkg_title': package['title'],
                                'name': resource['name'],
                                'id': resource['id'],
                                'total': resource_count,
                            }
                        )
                        total += resource_count

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
