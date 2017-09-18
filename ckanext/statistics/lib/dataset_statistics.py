import copy
from sqlalchemy import sql, case
from collections import OrderedDict
import ckan.logic as logic
from ckan.common import c
import ckan.model as model
from ckan.model.resource import Resource, ResourceGroup
from ckan.model.package import Package

from ckanext.statistics.model.datastore import DatastoreStat
from ckanext.statistics.lib.statistics import Statistics
from ckanext.statistics.logic.schema import statistics_dataset_schema

_check_access = logic.check_access
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError


class DatasetStatistics(Statistics):
    """
        Retrieve dataset statistics
    """

    schema = statistics_dataset_schema()

    def _get_statistics(self, year=None, month=None):
        """
        Fetch the statistics
        """
        year_part = sql.func.date_part('year', DatastoreStat.date).label('year')
        month_part = sql.func.date_part('month', DatastoreStat.date).label('month')

        rows = model.Session.query(
            sql.func.concat(month_part, '/', year_part).label("date"),
            sql.func.max(DatastoreStat.count).label("count"),
            Resource.id.label("resource_id"),
            Resource.name,
            Package.name.label('pkg_name'),
            Package.title.label('pkg_title'),
        ).join(Resource).join(ResourceGroup).join(Package).filter(
            Resource.state == 'active'
        ).filter(
            Package.state == 'active'
        ).group_by(
            year_part,
            month_part,
            Resource.id,
            Resource.name,
            Package.name,
            Package.title
        ).order_by(year_part, month_part)

        if year:
            rows = rows.filter(sql.extract('year', DatastoreStat.date) == year)
        if month:
            rows = rows.filter(sql.extract('month', DatastoreStat.date) == month)

        resource_id = self.params.get('resource_id', None)
        if resource_id:
            rows = rows.filter(Resource.id == resource_id)

        stats = {}
        context = {'model': model, 'user': c.user or c.author, 'auth_user_obj': c.userobj}

        for row in rows:
            try:
                _check_access('resource_show', context, row.__dict__)
            except NotAuthorized:
                pass
            else:
                stats.setdefault(row.__dict__['resource_id'], {
                    'id': row.__dict__['resource_id'],
                    'pkg_name': row.__dict__['pkg_name'],
                    'pkg_title': row.__dict__['pkg_title'],
                    'name': row.__dict__['name'],
                    'count': OrderedDict()
                })
                stats[row.__dict__['resource_id']]['count'][row.__dict__['date']] = row.__dict__['count']

        total = 0
        for s in stats.values():
            last_date = s['count'].keys()[-1]
            total += s['count'][last_date]

        return {
            'total': total,
            'resources': stats.values()
        }
