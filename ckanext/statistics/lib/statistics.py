# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


import abc

from ckan.plugins import toolkit


class Statistics(object):
    """
    Base class for the download and dataset statistics actions.

    :param context: Ckan execution context
    :param params: Dictionary containing the action parameters
    """

    def __init__(self, context, params):
        self.context = context
        self.params = params

    def validate(self):
        schema = self.context.get('schema', self.schema)
        self.params, errors = toolkit.navl_validate(self.params, schema, self.context)
        if errors:
            raise toolkit.ValidationError(errors)

    @abc.abstractproperty
    def schema(self):
        """
        Schema to validate against.

        :returns: the schema as a dict
        """
        return None

    @abc.abstractmethod
    def _get_statistics(self):
        """
        Get the statistics.

        :returns: dict of the requested stats
        """
        return None

    def get(self):
        """
        Fetch the statistics.
        """
        params = {k: self.params.get(k, None) for k in self.schema.keys()}
        return self._get_statistics(**params)
