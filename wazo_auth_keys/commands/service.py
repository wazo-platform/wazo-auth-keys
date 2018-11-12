# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os
import pwd
import uuid
import subprocess
import yaml

from cliff.command import Command

KEYS_PATH = '/var/lib/wazo-auth-keys'
FILENAME = os.path.join(KEYS_PATH, '{service_id}-key.yml')
DONT_CHANGE = -1

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

            self.update_file(name, password)

    def update_file(self, service_id, service_key):
        filename = FILENAME.format(service_id=service_id)
        self._system_user_map = {pw.pw_name: pw.pw_uid for pw in pwd.getpwall()}
        self._write_config_file(filename, service_id, service_key)
        self._change_ownership(filename, service_id)
        return filename

    def _change_ownership(self, filename, service_id):
        uid = self._system_user_map.get(service_id, DONT_CHANGE)
        os.chown(filename, uid, DONT_CHANGE)

    def _write_config_file(self, filename, service_id, service_key):
        self.app.LOG.debug('Writing %s ...', filename)
        with open(filename, 'w') as fobj:
            yaml.safe_dump({'service_id': service_id, 'service_key': service_key}, fobj)


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

        directory_files = os.listdir(KEYS_PATH)
        generated_files = [FILENAME.format(service_id=service_id) for service_id in CONFIG.keys()]
        for filename in directory_files:
            full_path = os.path.join(KEYS_PATH, filename)
            if full_path not in generated_files:
                self.app.LOG.debug('Removing %s ...', full_path)
                os.remove(full_path)
