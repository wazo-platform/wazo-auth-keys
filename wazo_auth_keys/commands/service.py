# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import json
import uuid
import subprocess

from cliff.command import Command

POLICY_NAME_TPL = '{username}-internal'

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
            help="Delete service before update it",
            action='store_true',
        )
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug('Parsed args: %s', parsed_args)

        for name, values in CONFIG.items():
            if parsed_args.recreate:
                self._delete_service(name)
                self.app.file_manager.remove(name)

            service_uuid = None
            if not self.app.file_manager.service_exists(name):
                password = str(uuid.uuid4())
                service_uuid = self._create_service(name, password)
                self.app.file_manager.update(name, password)

            service_uuid = service_uuid or self._get_service_uuid(name)
            self._update_service_policy(name, service_uuid, values['acl'])

    def _update_service_policy(self, username, service_uuid, acl):
        self._delete_service_policy(username)
        self._create_service_policy(username, service_uuid, acl)

    def _get_service_uuid(self, name):
        service = self.app.auth_cli('user', 'show', name, stderr=subprocess.DEVNULL)
        if not service:
            return
        service = json.loads(service)
        return service['uuid']

    def _delete_service(self, name):
        service_uuid = self._get_service_uuid(name)
        if not service_uuid:
            return

        self.app.auth_cli('user', 'delete', service_uuid, check=True)

    def _create_service(self, name, password):
        service_uuid = self.app.auth_cli(
            'user',
            'create',
            '--password', password,
            # '--tenant', wazo_auth_cli_tenant,
            name,
            check=True,
        )
        return service_uuid

    def _get_policy_uuid(self, name):
        policy = self.app.auth_cli('policy', 'show', name, stderr=subprocess.DEVNULL)
        if not policy:
            return
        policy = json.loads(policy)
        return policy['uuid']

    def _delete_service_policy(self, username):
        name = POLICY_NAME_TPL.format(username=username)
        policy_uuid = self._get_policy_uuid(name)
        if not policy_uuid:
            return

        self.app.auth_cli('policy', 'delete', policy_uuid, check=True)

    def _create_service_policy(self, username, service_uuid, acl):
        name = POLICY_NAME_TPL.format(username=username)
        args = []
        if acl:
            args = ['--acl', *acl]
        policy_uuid = self.app.auth_cli(
            'policy',
            'create',
            # '--tenant', wazo_auth_cli_tenant,
            name,
            *args,
            check=True,
        )

        self.app.auth_cli('user', 'add', '--policy', policy_uuid, service_uuid, check=True)


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
            raise NotImplementedError("'--users' is not implemented")

        self.app.file_manager.clean(excludes=list(CONFIG.keys()))
