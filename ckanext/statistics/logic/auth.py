# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK

from ckantools.decorators import auth


@auth(anon=True)
def download_statistics(context, data_dict):
    """
    Authorisation for the download_statistics action.
    """
    return {'success': True}


@auth(anon=True)
def dataset_statistics(context, data_dict):
    """
    Authorisation for the download_statistics action.
    """
    return {'success': True}
