
#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from ckan.plugins import toolkit

ignore_missing = toolkit.get_validator(u'ignore_missing')
int_validator = toolkit.get_validator(u'int_validator')
resource_id_exists = toolkit.get_validator(u'resource_id_exists')


def statistics_downloads_schema():
    '''Month and Year parameters

    :returns: schema

    '''
    schema = {
        u'month': [ignore_missing, int_validator],
        u'year': [ignore_missing, int_validator],
        }
    return schema


def statistics_dataset_schema():
    '''Resource ID

    :returns: schema

    '''
    schema = {
        u'resource_id': [ignore_missing, resource_id_exists],
        }
    return schema
