# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import subprocess
import sys
import yaml

from cliff.app import App
from cliff.commandmanager import CommandManager

from .file_manager import FileManager


class WazoAuthKeys(App):

    DEFAULT_VERBOSE_LEVEL = 999

    def __init__(self):
        super().__init__(
            description='A wrapper to wazo-auth-cli to manage internal users',
            command_manager=CommandManager('wazo_auth_keys.commands'),
            version='1.0.0',
        )
        self._auth_cli_exe = None

    def build_option_parser(self, *args, **kwargs):
        parser = super().build_option_parser(*args, **kwargs)
        parser.add_argument(
            '--wazo-auth-cli',
            default='/usr/bin/wazo-auth-cli',
            help='The wazo-auth-cli executable',
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

    def auth_cli(self, *args, **kwargs):
        self.LOG.debug('wazo-auth-cli %s ...', ' '.join(args))
        result = subprocess.run(
            [
                self._auth_cli_exe,
                '--token', self._token,
                *args,
            ],
            stdout=subprocess.PIPE,
            **kwargs,
        )
        return result.stdout.decode('utf-8').strip()

    def initialize_app(self, argv):
        self.LOG.debug('Wazo Auth Keys')
        self.LOG.debug('options=%s', self.options)
        with open(self.options.config, 'r') as f:
            self.services = yaml.load(f)
        self._auth_cli_exe = self.options.wazo_auth_cli
        self.file_manager = FileManager(self, self.options.base_dir)
        self._token = self._create_token()

    def _create_token(self):
        result = subprocess.run(
            [
                self._auth_cli_exe,
                '--config', '/root/.config/wazo-auth-cli',
                'token',
                'create',
                '--backend', 'wazo_user',
            ],
            check=True,
            stdout=subprocess.PIPE,
        )
        return result.stdout.decode('utf-8').strip()


def main(argv=sys.argv[1:]):
    app = WazoAuthKeys()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
