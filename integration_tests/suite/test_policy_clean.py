# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    assert_that,
    has_entries,
    has_items,
    not_,
)

from .helpers.base import BaseIntegrationTest


class TestPolicyClean(BaseIntegrationTest):

    asset = 'base'

    def test_remove_deprecated_policy(self):
        self._policy_update()
        self.auth.policies.new(name='policy-deprecated')

        self._policy_clean()

        policies = self.auth.policies.list()['items']
        assert_that(policies, not_(has_items(has_entries(name='policy-deprecated'))))
