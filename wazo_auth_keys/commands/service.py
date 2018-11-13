# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os
import uuid
import subprocess

from cliff.command import Command

KEYS_PATH = '/var/lib/wazo-auth-keys'
FILENAME = os.path.join(KEYS_PATH, '{service_id}-key.yml')

CONFIG = {
    'xivo-confd': {
        'acl': [
            'auth.users.#',
            'auth.admin.#',
        ],
    },
    'asterisk': {
        'acl': [
            'auth.tenants.read',
            'confd.voicemails.read',
            'confd.voicemails.*.read',
        ],
    }
}


class ServiceUpdate(Command):
    "Update all users defined in the config file"

    def get_parser(self, *args, **kwargs):
        parser = super().get_parser(*args, **kwargs)
        parser.add_argument(
            '--recreate',
            help="Delete service before create it",
            action='store_true',
        )
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug('Parsed args: %s', parsed_args)

        for name, acl in CONFIG.items():
            if parsed_args.recreate:
                if self.app.auth_cli('user', 'show', name, stderr=subprocess.DEVNULL):
                    if not self.app.auth_cli('user', 'delete', name):
                        self.app.LOG.warning('Unable to delete user: %s', name)
                        return

            password = str(uuid.uuid4())
            result = self.app.auth_cli(
                'user',
                'create',
                '--password', password,
                # '--tenant', wazo_auth_cli_tenant,
                name,
            )
            if not result:
                self.app.LOG.warning('Unable to create user: %s', name)
                return

            self.app.file_manager.update(name, password)


class ServiceClean(Command):
    "Clean undefined files"

    def get_parser(self, *args, **kwargs):
        parser = super().get_parser(*args, **kwargs)
        parser.add_argument(
            '--users',
            help="Delete undefined internal users",
            action='store_true',
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.users:
            self.app.LOG.debug('Delete all undefined internal users')
            raise NotImplementedError

        self.app.file_manager.clean(excludes=list(CONFIG.keys()))
