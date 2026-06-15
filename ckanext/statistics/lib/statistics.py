# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


import abc


class Statistics(object):
    """
    Base class for the download and dataset statistics actions.

    :param context: CKAN execution context
    """

    def __init__(self, context):
        self.context = context

    @abc.abstractmethod
    def get(self, **kwargs):
        """
        Fetch the statistics.
        """
        return {}
