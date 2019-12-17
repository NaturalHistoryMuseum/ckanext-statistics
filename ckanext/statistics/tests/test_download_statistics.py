# !/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-statistics
# Created by the Natural History Museum in London, UK


from collections import OrderedDict

import nose
import os
from ckanext.statistics.lib.download_statistics import DownloadStatistics
from ckantest.models import TestBase
from ckantest.factories.data import DataConstants

backfill_fn = u'data-portal-backfill.json'


class TestBackfillStatistics(TestBase):
    plugins = [u'statistics', u'versioned_datastore']

    @staticmethod
    def _backfill_fn_exists():
        fp = os.path.join(os.path.dirname(os.path.dirname(__file__)), u'data',
                          backfill_fn)
        return os.path.exists(fp)

    def test_no_backfill_json_file(self):
        backfill_stats = DownloadStatistics.backfill_stats(None)
        nose.tools.assert_equal(backfill_stats, {})

    def test_not_empty_if_file_given(self):
        backfill_stats = DownloadStatistics.backfill_stats(
            backfill_fn) if self._backfill_fn_exists() else {}
        assert self._backfill_fn_exists(), u'{0} does not exist'.format(
            backfill_fn)
        assert isinstance(backfill_stats, dict), u'is not a dictionary'
        assert len(backfill_stats) > 0, u'is empty'

    def test_filter_by_year(self):
        backfill_stats = {}
        yr = 2018
        while len(backfill_stats.keys()) == 0 and yr > 2013:
            yr -= 1
            backfill_stats = DownloadStatistics.backfill_stats(backfill_fn,
                                                               year=yr)
        assert len(backfill_stats.keys()) > 0, u'no results'
        assert all(
            [k.endswith('/{0}'.format(yr)) for k in backfill_stats.keys()])

    def test_filter_by_month(self):
        backfill_stats = {}
        mnth = 0
        while len(backfill_stats.keys()) == 0 and mnth < 12:
            mnth += 1
            backfill_stats = DownloadStatistics.backfill_stats(backfill_fn,
                                                               month=mnth)
        assert len(backfill_stats.keys()) > 0, u'no results'
        assert all(
            [k.startswith(u'{0}/'.format(mnth)) for k in backfill_stats.keys()])


class TestCkanPackagerStats(TestBase):
    plugins = [u'statistics', u'datastore', u'versioned_datastore']

    @classmethod
    def setup_class(cls):
        super(TestCkanPackagerStats, cls).setup_class()
        pkg_dict = cls.data_factory().package()
        cls._pkg_name = pkg_dict[u'name']
        res_dict_1 = cls.data_factory().resource(package_id=pkg_dict[u'id'], records=DataConstants.records)
        res_dict_2 = cls.data_factory().resource(package_id=pkg_dict[u'id'], records=DataConstants.records)
        cls._res_ids = [res_dict_1[u'id'], res_dict_2[u'id']]

    def test_no_resource_ids(self):
        self.config.remove(u'ckanext.statistics.resource_ids')
        ckan_stats = DownloadStatistics.ckanpackager_stats()
        nose.tools.assert_equal(len(ckan_stats), 0)

    def test_with_resource_ids(self):
        self.config.update({u'ckanext.statistics.resource_ids': self._res_ids[0]})
        ckan_stats = DownloadStatistics.ckanpackager_stats()
        nose.tools.assert_equal(len(ckan_stats), 0)


class TestMerge(TestBase):
    plugins = [u'statistics', u'versioned_datastore']

    @classmethod
    def setup_class(cls):
        super(TestMerge, cls).setup_class()
        cls.ckan_stats = DownloadStatistics.ckanpackager_stats()
        cls.backfill_stats = DownloadStatistics.backfill_stats(backfill_fn)
        cls.merged_stats = DownloadStatistics.merge(cls.ckan_stats, cls.backfill_stats)

    def test_ordereddict_output(self):
        assert isinstance(self.merged_stats,
                          OrderedDict), u'merge result is {0}, ' \
                                        u'not OrderedDict'.format(
            type(self.merged_stats))

    def test_all_keys_present(self):
        bf_keys_in_merge = [(k in self.merged_stats.keys()) for k in
                            self.backfill_stats.keys()]
        ck_keys_in_merge = [(k in self.merged_stats.keys()) for k in
                            self.ckan_stats.keys()]
        assert all(
            ck_keys_in_merge), u'not all ckanpackager keys are present in the ' \
                               u'merged output'
        assert all(
            bf_keys_in_merge), u'not all backfill keys are present in the merged output'
