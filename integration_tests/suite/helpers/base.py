# Copyright 2018-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import yaml

from wazo_auth_client import Client as AuthClient
from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase

ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets'))

USERNAME = 'wazo-auth-cli'
PASSWORD = 'secret'


class BaseIntegrationTest(AssetLaunchingTestCase):

    assets_root = ASSETS
    service = 'auth-keys'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_auth()

    @classmethod
    def setup_auth(cls):
        cls.auth = cls.new_auth(username=USERNAME, password=PASSWORD)
        token = cls.auth.token.new('wazo_user', expiration=3600)
        cls.auth.set_token(token['token'])

    @classmethod
    def new_auth(cls, **kwargs):
        return AuthClient(
            '127.0.0.1',
            cls.service_port(9497, 'auth'),
            prefix=None,
            https=False,
            **kwargs
        )

    def _print_to_container_log(self, result):
        command = ['/bin/bash', '-c', f'echo {result} &> /proc/1/fd/1']
        self.docker_exec(command, service_name='auth-keys')

    def _service_clean(self, users=False):
        flags = []
        if users:
            flags.append('--users')

        output = self.docker_exec(['wazo-auth-keys', 'service', 'clean', *flags])
        result = output.decode('utf-8')
        self._print_to_container_log('_service_clean result:\n{}'.format(result))
        return result

    def _service_update(self, recreate=False):
        flags = []
        if recreate:
            flags.append('--recreate')

        output = self.docker_exec(['wazo-auth-keys', 'service', 'update', *flags])
        result = output.decode('utf-8')
        self._print_to_container_log('_service_update result:\n{}'.format(result))
        return result

    def _list_filenames(self):
        output = self.docker_exec(['ls', '/var/lib/wazo-auth-keys'])
        result = output.decode('utf-8').split()
        self._print_to_container_log('_list_filenames result: {}'.format(result))
        return result

    def _get_owner(self, filename):
        output = self.docker_exec(
            ['stat', '-c', '%U', '/var/lib/wazo-auth-keys/{}'.format(filename)]
        )
        result = output.decode('utf-8').strip()
        self._print_to_container_log('_get_owner filename: {}, result: {}'.format(filename, result))
        return result

    def _create_filename(self, filename):
        self.docker_exec(['touch', '/var/lib/wazo-auth-keys/{}'.format(filename)])

    def _delete_filename(self, filename):
        self.docker_exec(['rm', '/var/lib/wazo-auth-keys/{}'.format(filename)])

    def _copy_override_filename(self, filename):
        override_path = 'etc/wazo-auth-keys/conf.d/{}'.format(filename)
        self.docker_copy_to_container(
            os.path.join(ASSETS, override_path), '/{}'.format(override_path)
        )

    def _delete_override_filename(self, filename):
        self.docker_exec(['rm', '/etc/wazo-auth-keys/conf.d/{}'.format(filename)])

    def _get_last_modification_time(self, filename):
        output = self.docker_exec(
            ['stat', '-c', '%Y', '/var/lib/wazo-auth-keys/{}'.format(filename)]
        )
        result = output.decode('utf-8')
        self._print_to_container_log(
            '_get_last_modification_time filename: {}, result: {}'.format(
                filename, result
            )
        )
        return result

    def _get_service_config(self, service_name):
        output = self.docker_exec(
            ['cat', '/var/lib/wazo-auth-keys/{}-key.yml'.format(service_name)]
        )
        result = yaml.safe_load(output.decode('utf-8'))
        self._print_to_container_log(
            '_get_service_config sevrice: {}, result: {}'.format(service_name, result)
        )
        return result

    def _delete_service(self, username):
        services = self.auth.users.list(username=username)['items']
        if not services:
            return
        self.auth.users.delete(services[0]['uuid'])
