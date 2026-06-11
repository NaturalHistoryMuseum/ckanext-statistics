# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from ckan.plugins import SingletonPlugin, implements, interfaces
from ckantools.cache import configure_cache
from ckantools.loaders import create_actions, create_auth

from ckanext.statistics.logic import (
    action as statistics_actions,
)
from ckanext.statistics.logic import (
    auth as statistics_auth,
)


class StatisticsPlugin(SingletonPlugin):
    """
    NHM Statistics.
    """

    implements(interfaces.IActions)
    implements(interfaces.IAuthFunctions)
    implements(interfaces.IConfigurable)

    # IActions
    def get_actions(self):
        return create_actions(statistics_actions)

    # IAuthFunctions
    def get_auth_functions(self):
        return create_auth(statistics_auth)

    # IConfigurable
    def configure(self, config):
        # configure cache
        configure_cache(config, 'statistics', ['statistics_short', 'statistics_long'])
