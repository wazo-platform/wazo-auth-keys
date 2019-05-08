# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    contains_inanyorder,
    empty,
    equal_to,
    has_entries,
    has_items,
    not_,
)

from .helpers.base import BaseIntegrationTest


class TestPolicyUpdate(BaseIntegrationTest):

    asset = 'base'

    def setUp(self):
        super().setUp()
        self._policy_update(recreate=True)

    def test_create_policy(self):
        self._policy_update()

        policies = self.auth.policies.list()['items']
        assert_that(
            policies,
            has_items(
                has_entries(
                    name='policy-empty',
                    acl_templates=empty(),
                ),
                has_entries(
                    name='policy-standard',
                    acl_templates=contains_inanyorder(
                        'random.acl.*',
                        'weird.random.#',
                        'another.random.read',
                    ),
                ),
            )
        )

    def test_do_not_recreate_policy(self):
        policy_name = 'policy-standard'
        created_policy = self.auth.policies.list(name=policy_name)['items'][0]

        self._policy_update()

        updated_policy = self.auth.policies.list(name=policy_name)['items'][0]
        assert_that(updated_policy['uuid'], equal_to(created_policy['uuid']))

    def test_update_policies(self):
        policy_name = 'policy-standard'
        policy_uuid = self.auth.policies.list(name=policy_name)['items'][0]['uuid']
        self.auth.policies.edit(
            policy_uuid,
            name=policy_name,
            acl_templates=['break.all.acl']
        )

        self._policy_update()

        policy = self.auth.policies.get(policy_uuid)
        assert_that(
            policy,
            has_entries(
                name=policy_name,
                acl_templates=contains_inanyorder(
                    'random.acl.*',
                    'weird.random.#',
                    'another.random.read',
                ),
            ),
        )

    def test_recreate_user_when_flag_recreate(self):
        policy_name = 'policy-standard'
        created_policy = self.auth.policies.list(name=policy_name)['items'][0]

        self._policy_update(recreate=True)

        updated_policy = self.auth.policies.list(name=policy_name)['items'][0]
        assert_that(updated_policy['uuid'], not_(equal_to(created_policy['uuid'])))
