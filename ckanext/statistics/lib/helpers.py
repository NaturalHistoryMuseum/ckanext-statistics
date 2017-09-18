#!/usr/bin/env python
# encoding: utf-8
"""
Created by Ben Scott on '16/09/2017'.
"""

import ckan.model as model
from ckan.common import c
import ckan.logic as logic

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError

get_action = logic.get_action
_check_access = logic.check_access


def get_datastore_stats():
    context = {'model': model, 'user': c.user or c.author, 'auth_user_obj': c.userobj}




    stats = {
        'resources': [],
        'total': 0,
        'date': None,
    }

    resource_counts = model.Session.execute(
        """
        SELECT r.id, r.name, d.count, d.date, p.id AS pkg_id, p.title AS pkg_title, p.name AS pkg_name
        FROM resource r
        INNER JOIN datastore_stats d ON r.id = d.resource_id
        INNER JOIN resource_group rg ON r.resource_group_id = rg.id
        INNER JOIN package p ON rg.package_id = p.id
        WHERE r.state='active' AND p.state='active' AND date = (SELECT date FROM datastore_stats ORDER BY date DESC LIMIT 1)
        ORDER BY count DESC
        """
    )

    for resource in resource_counts:
        try:
            _check_access('resource_show', context, dict(resource))
        except NotAuthorized:
            pass
        else:
            stats['resources'].append(resource)
            stats['total'] += int(resource['count'])
            stats['date'] = resource['date']

    return stats
