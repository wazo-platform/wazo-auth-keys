# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os

from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase
from xivo_auth_client import Client as AuthClient

ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets'))
KEY_FILENAME = os.path.join(ASSETS, 'init-auth-key')


class BaseIntegrationTest(AssetLaunchingTestCase):

    assets_root = ASSETS
    service = 'auth-keys'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.complete_wazo_auth_bootstrap()

    @classmethod
    def complete_wazo_auth_bootstrap(cls):
        with open(KEY_FILENAME, 'r') as f:
            for line in f:
                key = line.strip()
                break

        body = {
            'key': key,
            'username': 'wazo-auth-cli',
            'password': 'secret',
            'purpose': 'internal',
        }
        auth = AuthClient('localhost', cls.service_port(9497, 'auth'), verify_certificate=False)
        auth.init.run(**body)
