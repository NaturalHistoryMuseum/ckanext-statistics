import os
import json
from logging import getLogger
import ckan.plugins as p

log = getLogger(__name__)
ignore_empty = p.toolkit.get_validator('ignore_empty')


class StatsPlugin(p.SingletonPlugin):
    """
    Summary dataset view
    Provides a summary view of records, to replace the grid
    """



