# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_entries,
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

    def test_remove_undefined_service(self):
        self._service_update()
        self.auth.users.new(username='undefined', purpose='internal')

        self._service_clean(users=True)

        users = self.auth.users.list(purpose='internal')['items']
        assert_that(users, not_(has_items(has_entries(username='undefined'))))

    def test_does_not_remove_wazo_auth_cli(self):
        self._service_clean(users=True)

        users = self.auth.users.list(purpose='internal')['items']
        assert_that(users, has_items(has_entries(username='wazo-auth-cli')))
