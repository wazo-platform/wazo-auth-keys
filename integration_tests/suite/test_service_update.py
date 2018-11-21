# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import (
    assert_that,
    contains_inanyorder,
    has_entries,
    has_items,
)

from .helpers.base import BaseIntegrationTest


class TestServiceUpdate(BaseIntegrationTest):

    asset = 'base'

    def _service_update(self):
        output = self.docker_exec(['wazo-auth-keys', 'service', 'update'])
        result = output.decode('utf-8')
        print('_service_update result:\n{}'.format(result))
        return result

    def _list_filenames(self):
        output = self.docker_exec(['ls', '/var/lib/wazo-auth-keys'])
        result = output.decode('utf-8').split()
        print('_list_filenames result: {}'.format(result))
        return result

    def test_create_user(self):
        self._service_update()
        filenames = self._list_filenames()
        assert_that(
            filenames,
            contains_inanyorder(
                'service-anonymous-key.yml',
                'service-hashtag-key.yml',
                'service-standard-key.yml',
            )
        )

        users = self.auth.users.list()['items']
        assert_that(
            users,
            has_items(
                has_entries(username='service-anonymous'),
                has_entries(username='service-hashtag'),
                has_entries(username='service-standard'),
            )
        )

    def test_do_not_recreate_user(self):
        pass

    def test_create_policies(self):
        pass

    def test_update_policies(self):
        pass

    def test_recreate_user_when_flag_recreate(self):
        pass
