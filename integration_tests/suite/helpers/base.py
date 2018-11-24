# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os
import yaml

from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase
from xivo_auth_client import Client as AuthClient

ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets'))
KEY_FILENAME = os.path.join(ASSETS, 'init-auth-key')

USERNAME = 'wazo-auth-cli'
PASSWORD = 'secret'


class BaseIntegrationTest(AssetLaunchingTestCase):

    assets_root = ASSETS
    service = 'auth-keys'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.complete_wazo_auth_bootstrap()
        cls.setup_auth()

    @classmethod
    def complete_wazo_auth_bootstrap(cls):
        with open(KEY_FILENAME, 'r') as f:
            for line in f:
                key = line.strip()
                break

        body = {
            'key': key,
            'username': USERNAME,
            'password': PASSWORD,
            'purpose': 'internal',
        }
        cls.new_auth().init.run(**body)

    @classmethod
    def setup_auth(cls):
        cls.auth = cls.new_auth(username=USERNAME, password=PASSWORD)
        token = cls.auth.token.new('wazo_user', expiration=3600)
        cls.auth.set_token(token['token'])

    @classmethod
    def new_auth(cls, **kwargs):
        return AuthClient('localhost', cls.service_port(9497, 'auth'), verify_certificate=False, **kwargs)

    def _service_clean(self, users=False):
        flags = []
        if users:
            flags.append('--users')

        output = self.docker_exec(['wazo-auth-keys', 'service', 'clean', *flags])
        result = output.decode('utf-8')
        print('_service_clean result:\n{}'.format(result))
        return result

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

    def _create_filename(self, filename):
        self.docker_exec(['touch', '/var/lib/wazo-auth-keys/{}'.format(filename)])

    def _delete_filename(self, filename):
        self.docker_exec(['rm', '/var/lib/wazo-auth-keys/{}'.format(filename)])

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

    def _delete_service(self, username):
        services = self.auth.users.list(username=username)['items']
        if not services:
            return
        self.auth.users.delete(services[0]['uuid'])
