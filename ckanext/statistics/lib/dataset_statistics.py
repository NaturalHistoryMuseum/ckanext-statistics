import ckan.logic as logic
from ckan.common import c, _
import ckan.model as model
import logging
import ckan.plugins as p
import ckan.lib.base as base
from ckan.lib.search import SearchIndexError

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
    """
        Retrieve dataset statistics
    """

    schema = statistics_dataset_schema()

    def _get_statistics(self, resource_id=None):
        """
        Fetch the statistics
        """
        context = {'model': model, 'user': c.user or c.author, 'auth_user_obj': c.userobj}
        if resource_id:
            return self._get_resource_statistics(resource_id, context)
        else:
            return self._get_all_resources_statistics(context)

    @staticmethod
    def _get_all_resources_statistics(context):

        stats = {
            'total': 0,
            'resources': []
        }

        pkgs = p.toolkit.get_action('current_package_list_with_resources')(context, {'limit': 200})
        for pkg_dict in pkgs:
            if pkg_dict['private'] or pkg_dict['state'] != 'active':
                continue

            if 'resources' in pkg_dict:
                for resource in pkg_dict['resources']:
                    if resource['state'] != 'active':
                        continue
                    # Does this have an activate datastore table?
                    if resource['url_type'] in ['datastore', 'upload', 'dataset']:
                        data = {
                            'resource_id': resource['id'],
                            'limit': 1
                        }
                        try:
                            search = p.toolkit.get_action('datastore_search')({}, data)
                        except (logic.NotFound, SearchIndexError):
                            # Not every file is uploaded to the datastore, so ignore it
                            continue

                        stats['resources'].append(
                            {
                                'pkg_name': pkg_dict['name'],
                                'pkg_title': pkg_dict['title'],
                                'name': resource['name'],
                                'id': resource['id'],
                                'total': search.get('total', 0)
                            }
                        )
                        stats['total'] += search.get('total', 0)
        return stats

    def _get_resource_statistics(self, resource_id, context):
        """
        Get stats for an individual resource
        @param resource_id:
        @return:
        """
        try:
            resource = get_action('resource_show')(self.context, {'id': resource_id})
        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % resource_id)
        else:

            # TODO - Add break down over time for SOLR Datasets
            # k = 'ckanext.datasolr.'
            # solr_datasets = [c.replace(k, '') for c in pylons.config.keys() if k in c]
            # facet.date=created&facet.date.start=2010-01-01T00:00:00.000Z&facet.date.end=NOW&facet.date.gap=%2B1MONTH
            search = p.toolkit.get_action('datastore_search')({}, {'resource_id': resource_id, 'limit': 1})

            return {
                'resource': resource,
                'total': search['total']
            }
