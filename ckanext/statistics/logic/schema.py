#!/usr/bin/env python
# encoding: utf-8
"""
Created by 'bens3' on 2013-06-21.
Copyright (c) 2013 'bens3'. All rights reserved.
"""

import ckan.plugins as p
from ckanext.datastore.logic.schema import datastore_search_schema as ckan_datastore_search_schema
from ckanext.datastore.logic.schema import list_of_strings_or_string, json_validator

get_validator = p.toolkit.get_validator

ignore_missing = get_validator('ignore_missing')
int_validator = get_validator('int_validator')
resource_id_exists = get_validator('resource_id_exists')


def list_of_resource_ids(key, data, errors, context):
    value = data.get(key)
    if isinstance(value, basestring):
        value = [value]

    for resource_id in value:
        resource_id_exists(resource_id, context)


def statistics_downloads_schema():
    """
    Month and Year parameters
    :return: schema
    """
    schema = {
        'month': [ignore_missing, int_validator],
        'year': [ignore_missing, int_validator],
        'resource_id': [ignore_missing, list_of_resource_ids],
    }
    return schema


def statistics_dataset_schema():
    """
    Resource ID
    :return: schema
    """
    schema = {
        'resource_id': [ignore_missing, resource_id_exists],
    }
    return schema
