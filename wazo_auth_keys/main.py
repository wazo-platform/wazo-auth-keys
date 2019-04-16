# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import sys
import yaml

from cliff.app import App
from cliff.commandmanager import CommandManager

from xivo_auth_client import Client

from . import config
from .file_manager import FileManager


class WazoAuthKeys(App):

    DEFAULT_VERBOSE_LEVEL = 0

    def __init__(self):
        super().__init__(
            description='A wrapper to wazo-auth-cli to manage internal users',
            command_manager=CommandManager('wazo_auth_keys.commands'),
            version='1.0.0',
        )
        self._token = None
        self._client = None

    def build_option_parser(self, *args, **kwargs):
        parser = super().build_option_parser(*args, **kwargs)
        parser.add_argument(
            '--wazo-auth-cli-config',
            default=os.getenv('WAZO_AUTH_CLI_CONFIG', '/root/.config/wazo-auth-cli'),
            help='Extra configuration directory to override the wazo-auth-cli configuration',
        )
        parser.add_argument(
            '--base-dir',
            default='/var/lib/wazo-auth-keys',
            help='The base directory of the file keys',
        )
        parser.add_argument(
            '--config',
            default='/etc/wazo-auth-keys/config.yml',
            help='The wazo-auth-keys configuration file',
        )
        return parser

    @property
    def client(self):
        if not self._client:
            self._client = Client(**self._auth_config)

        if not self._token:
            self._token = self._client.token.new('wazo_user', expiration=600)['token']

        self._client.set_token(self._token)
        return self._client

    def initialize_app(self, argv):
        self.LOG.debug('wazo-auth-keys')
        self.LOG.debug('options=%s', self.options)

        conf = config.build(self.options)
        self.LOG.debug('Starting with config: %s', conf)

        self.LOG.debug('client args: %s', conf['auth'])
        self._auth_config = dict(conf['auth'])

        with open(self.options.config, 'r') as f:
            self.services = yaml.safe_load(f)
        self.file_manager = FileManager(self, self.options.base_dir)


def main(argv=sys.argv[1:]):
    app = WazoAuthKeys()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
