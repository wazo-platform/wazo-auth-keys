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
            **kwargs,
        )

    def _print_to_container_log(self, result):
        cmd = ['/bin/bash', '-c', f'echo {result} &> /proc/1/fd/1']
        self.docker_exec(cmd)

    def _service_clean(self, users=False):
        flags = []
        if users:
            flags.append('--users')

        cmd = ['wazo-auth-keys', 'service', 'clean', *flags]
        output = self.docker_exec(cmd)
        result = output.decode('utf-8')
        log = f'_service_clean result:\n{result}'
        self._print_to_container_log(log)
        return result

    def _service_update(self, recreate=False):
        flags = []
        if recreate:
            flags.append('--recreate')

        cmd = ['wazo-auth-keys', 'service', 'update', *flags]
        output = self.docker_exec(cmd)
        result = output.decode('utf-8')
        log = f'_service_update result:\n{result}'
        self._print_to_container_log(log)
        return result

    def _list_filenames(self):
        cmd = ['ls', '/var/lib/wazo-auth-keys']
        output = self.docker_exec(cmd)
        result = output.decode('utf-8').split()
        log = f'_list_filenames result: {result}'
        self._print_to_container_log(log)
        return result

    def _get_owner(self, filename):
        cmd = ['stat', '-c', '%U', f'/var/lib/wazo-auth-keys/{filename}']
        output = self.docker_exec(cmd)
        result = output.decode('utf-8').strip()
        log = f'_get_owner filename: {filename}, result: {result}'
        self._print_to_container_log(log)
        return result

    def _create_filename(self, filename):
        cmd = ['touch', f'/var/lib/wazo-auth-keys/{filename}']
        self.docker_exec(cmd)

    def _delete_filename(self, filename):
        cmd = ['rm', f'/var/lib/wazo-auth-keys/{filename}']
        self.docker_exec(cmd)

    def _copy_override_filename(self, filename):
        override_path = f'etc/wazo-auth-keys/conf.d/{filename}'
        self.docker_copy_to_container(
            os.path.join(ASSETS, override_path),
            f'/{override_path}',
        )

    def _delete_override_filename(self, filename):
        self.docker_exec(['rm', f'/etc/wazo-auth-keys/conf.d/{filename}'])

    def _get_last_modification_time(self, filename):
        cmd = ['stat', '-c', '%Y', f'/var/lib/wazo-auth-keys/{filename}']
        output = self.docker_exec(cmd)
        result = output.decode('utf-8')
        log = f'_get_last_modification_time filename: {filename}, result: {result}'
        self._print_to_container_log(log)
        return result

    def _get_service_config(self, service_name):
        cmd = ['cat', f'/var/lib/wazo-auth-keys/{service_name}-key.yml']
        output = self.docker_exec(cmd)
        result = yaml.safe_load(output.decode('utf-8'))
        log = f'_get_service_config sevrice: {service_name}, result: {result}'
        self._print_to_container_log(log)
        return result

    def _delete_service(self, username):
        services = self.auth.users.list(username=username)['items']
        if not services:
            return
        self.auth.users.delete(services[0]['uuid'])
