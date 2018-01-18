
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK

import ckan.plugins as p
from ckanext.datastore.logic.schema import datastore_search_schema as ckan_datastore_search_schema
from ckanext.datastore.logic.schema import list_of_strings_or_string, json_validator

get_validator = p.toolkit.get_validator

ignore_missing = get_validator(u'ignore_missing')
int_validator = get_validator(u'int_validator')
resource_id_exists = get_validator(u'resource_id_exists')


def statistics_downloads_schema():
    '''
    Month and Year parameters
    :return: schema
    '''
    schema = {
        u'month': [ignore_missing, int_validator],
        u'year': [ignore_missing, int_validator],
    }
    return schema


def statistics_dataset_schema():
    '''
    Resource ID
    :return: schema
    '''
    schema = {
        u'resource_id': [ignore_missing, resource_id_exists],
    }
    return schema
