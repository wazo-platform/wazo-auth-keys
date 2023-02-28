# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    contains_string,
    empty,
    equal_to,
    has_entries,
    has_items,
    not_,
)

from .helpers.base import BaseIntegrationTest


class TestServiceUpdate(BaseIntegrationTest):
    asset = 'base'

    def setUp(self):
        super().setUp()
        self._service_update(recreate=True)

    def test_create_file_and_user_and_policy(self):
        self._service_update()
        filenames = self._list_filenames()
        assert_that(
            filenames,
            contains_inanyorder(
                'service-anonymous-key.yml',
                'service-hashtag-key.yml',
                'service-standard-key.yml',
            ),
        )

        owner = self._get_owner('service-anonymous-key.yml')
        assert_that(owner, equal_to('root'))

        owner = self._get_owner('service-hashtag-key.yml')
        assert_that(owner, equal_to('my-custom-user'))

        owner = self._get_owner('service-standard-key.yml')
        assert_that(owner, equal_to('root'))

        users = self.auth.users.list()['items']
        assert_that(
            users,
            has_items(
                has_entries(username='service-anonymous'),
                has_entries(username='service-hashtag'),
                has_entries(username='service-standard'),
            ),
        )

        policies = self.auth.policies.list()['items']
        assert_that(
            policies,
            has_items(
                has_entries(
                    name='service-anonymous-internal',
                    acl=empty(),
                ),
                has_entries(
                    name='service-hashtag-internal',
                    acl=contains_inanyorder('#'),
                ),
                has_entries(
                    name='service-standard-internal',
                    acl=contains_inanyorder(
                        'random.acl.*',
                        'weird.random.#',
                        'another.random.read',
                    ),
                ),
            ),
        )

    def test_do_not_recreate_user(self):
        expected_time = self._get_last_modification_time('service-anonymous-key.yml')

        self._service_update()

        modification_time = self._get_last_modification_time(
            'service-anonymous-key.yml'
        )
        assert_that(modification_time, equal_to(expected_time))

        credential = self._get_service_config('service-anonymous')
        auth = self.new_auth(
            username=credential['service_id'], password=credential['service_key']
        )
        auth.token.new('wazo_user')

    def test_update_policies(self):
        service_name = 'service-standard-internal'
        policy_uuid = self.auth.policies.list(name=service_name)['items'][0]['uuid']
        self.auth.policies.edit(policy_uuid, name=service_name, acl=['break.all.acl'])

        self._service_update()

        policies = self.auth.policies.list()['items']
        assert_that(
            policies,
            has_items(
                has_entries(
                    name=service_name,
                    acl=contains_inanyorder(
                        'random.acl.*',
                        'weird.random.#',
                        'another.random.read',
                    ),
                ),
            ),
        )

    def test_recreate_user_when_flag_recreate(self):
        first_modification_time = self._get_last_modification_time(
            'service-anonymous-key.yml'
        )

        self._service_update(recreate=True)

        modification_time = self._get_last_modification_time(
            'service-anonymous-key.yml'
        )
        assert_that(modification_time, not_(equal_to(first_modification_time)))

        credential = self._get_service_config('service-anonymous')
        auth = self.new_auth(
            username=credential['service_id'], password=credential['service_key']
        )
        auth.token.new('wazo_user')

    def test_when_file_exists_without_user(self):
        self._create_filename('service-anonymous-key.yml')
        self._delete_service('service-anonymous')

        log = self._service_update()

        assert_that(log, contains_string("Please use '--recreate'"))

    def test_when_user_exists_without_file(self):
        self._delete_filename('service-anonymous-key.yml')

        log = self._service_update()

        assert_that(log, contains_string("Please use '--recreate'"))

    def test_override_policies(self):
        self._copy_override_filename('override.yml')

        self._service_update(recreate=True)

        users = self.auth.users.list()['items']
        assert_that(
            users,
            has_items(
                has_entries(username='service-anonymous'),
                has_entries(username='service-hashtag'),
                has_entries(username='service-standard'),
                has_entries(username='service-additional'),
            ),
        )

        policies = self.auth.policies.list()['items']
        assert_that(
            policies,
            has_items(
                has_entries(
                    name='service-hashtag-internal',
                    acl=contains_inanyorder(
                        '#',
                        'additional.acl',
                    ),
                ),
                has_entries(
                    name='service-additional-internal',
                    acl=contains_inanyorder('#'),
                ),
            ),
        )

        self._delete_override_filename('override.yml')
        self._service_update(recreate=True)
