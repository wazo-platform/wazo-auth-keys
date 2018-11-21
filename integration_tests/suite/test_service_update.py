# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import yaml

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


class TestServiceUpdate(BaseIntegrationTest):

    asset = 'base'

    def _service_update(self, recreate=False):
        flags = []
        if recreate:
            flags.append('--recreate')

        output = self.docker_exec(['wazo-auth-keys', 'service', 'update', *flags])
        result = output.decode('utf-8')
        print('_service_update result:\n{}'.format(result))
        return result

    def _list_filenames(self):
        output = self.docker_exec(['ls', '/var/lib/wazo-auth-keys'])
        result = output.decode('utf-8').split()
        print('_list_filenames result: {}'.format(result))
        return result

    def _get_last_modification_time(self, filename):
        output = self.docker_exec([
            'stat',
            '-c',
            '%Y',
            '/var/lib/wazo-auth-keys/{}'.format(filename)
        ])
        result = output.decode('utf-8')
        print('_get_last_modification_time filename: {}, result: {}'.format(filename, result))
        return result

    def _get_service_config(self, service_name):
        output = self.docker_exec([
            'cat',
            '/var/lib/wazo-auth-keys/{}-key.yml'.format(service_name)
        ])
        result = yaml.load(output.decode('utf-8'))
        print('_get_service_config sevrice: {}, result: {}'.format(service_name, result))
        return result

    def test_create_file_and_user_and_policy(self):
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

        policies = self.auth.policies.list()['items']
        assert_that(
            policies,
            has_items(
                has_entries(
                    name='service-anonymous-internal',
                    acl_templates=empty(),
                ),
                has_entries(
                    name='service-hashtag-internal',
                    acl_templates=contains_inanyorder(
                        '#'
                    ),
                ),
                has_entries(
                    name='service-standard-internal',
                    acl_templates=contains_inanyorder(
                        'random.acl.*',
                        'weird.random.#',
                        'another.random.read',
                    ),
                ),
            )
        )

    def test_do_not_recreate_user(self):
        self._service_update()
        expected_time = self._get_last_modification_time('service-anonymous-key.yml')

        self._service_update()

        modification_time = self._get_last_modification_time('service-anonymous-key.yml')
        assert_that(modification_time, equal_to(expected_time))

        credential = self._get_service_config('service-anonymous')
        auth = self.new_auth(username=credential['service_id'], password=credential['service_key'])
        auth.token.new('wazo_user')

    def test_update_policies(self):
        service_name = 'service-standard-internal'
        self._service_update()
        policy_uuid = self.auth.policies.list(name=service_name)['items'][0]['uuid']
        self.auth.policies.edit(
            policy_uuid,
            name=service_name,
            acl_templates=['break.all.acl']
        )

        self._service_update()

        policies = self.auth.policies.list()['items']
        assert_that(
            policies,
            has_items(
                has_entries(
                    name=service_name,
                    acl_templates=contains_inanyorder(
                        'random.acl.*',
                        'weird.random.#',
                        'another.random.read',
                    ),
                ),
            )
        )

    def test_recreate_user_when_flag_recreate(self):
        self._service_update()
        first_modification_time = self._get_last_modification_time('service-anonymous-key.yml')

        self._service_update(recreate=True)

        modification_time = self._get_last_modification_time('service-anonymous-key.yml')
        assert_that(modification_time, not_(equal_to(first_modification_time)))

        credential = self._get_service_config('service-anonymous')
        auth = self.new_auth(username=credential['service_id'], password=credential['service_key'])
        auth.token.new('wazo_user')
