# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    has_items,
    not_,
)

from .helpers.base import BaseIntegrationTest


class TestServiceClean(BaseIntegrationTest):

    asset = 'base'

    def test_remove_undefined_files(self):
        self._create_filename('undefined-key.yml')

        self._service_clean()

        filenames = self._list_filenames()
        assert_that(filenames, not_(has_items('undefined-key.yml')))

    def test_remove_undefined_internal_user(self):
        # NotImplemented
        pass
