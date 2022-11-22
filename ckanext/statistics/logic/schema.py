# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from ckan.plugins import toolkit

ignore_missing = toolkit.get_validator('ignore_missing')
int_validator = toolkit.get_validator('int_validator')
resource_id_exists = toolkit.get_validator('resource_id_exists')


def list_of_resource_ids(key, data, errors, context):
    value = data.get(key)
    if isinstance(value, str):
        value = [value]

    for resource_id in value:
        resource_id_exists(resource_id, context)


def statistics_downloads_schema():
    """
    Month and Year parameters.

    :returns: schema
    """
    schema = {
        'month': [ignore_missing, int_validator],
        'year': [ignore_missing, int_validator],
        'resource_id': [ignore_missing, list_of_resource_ids],
    }
    return schema


def statistics_dataset_schema():
    """
    Resource ID.

    :returns: schema
    """
    schema = {
        'resource_id': [ignore_missing, resource_id_exists],
    }
    return schema
