# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import subprocess
import sys

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
        return parser

    def auth_cli(self, *args, **kwargs):
        self.LOG.debug('wazo-auth-cli %s ...', ' '.join(args))
        return_code = subprocess.call(
            [
                self._auth_cli_exe,
                '--config', '/root/.config/wazo-auth-cli',
                *args,
            ],
            stdout=subprocess.DEVNULL,
            **kwargs,
        )
        return return_code == 0

    def initialize_app(self, argv):
        self.LOG.debug('Wazo Auth Keys')
        self.LOG.debug('options=%s', self.options)
        self._auth_cli_exe = self.options.wazo_auth_cli
        self.file_manager = FileManager(self, self.options.base_dir)
        # TODO check config with: wazo-auth-cli status

    def clean_up(self, cmd, result, err):
        if err:
            self.LOG.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    app = WazoAuthKeys()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
