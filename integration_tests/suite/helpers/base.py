# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os

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
        auth = AuthClient('localhost', cls.service_port(9497, 'auth'), verify_certificate=False)
        auth.init.run(**body)

    @classmethod
    def setup_auth(cls):
        cls.auth = AuthClient(
            'localhost',
            cls.service_port(9497, 'auth'),
            username=USERNAME,
            password=PASSWORD,
            verify_certificate=False,
        )
        token = cls.auth.token.new('wazo_user', expiration=3600)
        cls.auth.set_token(token['token'])
