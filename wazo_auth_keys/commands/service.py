# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import uuid

from cliff.command import Command

POLICY_NAME_TPL = '{username}-internal'


class ServiceUpdate(Command):
    "Update or create all users defined in the config file"

    def get_parser(self, *args, **kwargs):
        parser = super().get_parser(*args, **kwargs)
        parser.add_argument(
            '--recreate', help="Delete service before updating it", action='store_true',
        )
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug('Parsed args: %s', parsed_args)

        for name, values in self.app.services.items():
            if parsed_args.recreate:
                self._delete_service(name)
                self._delete_policy(name)
                self.app.file_manager.remove(name)

            service_uuid = self._find_service_uuid(name)
            if not self.app.file_manager.service_exists(name):
                if service_uuid:
                    raise RuntimeError(
                        (
                            "User ({}) exists but not the file associated. "
                            "Please use '--recreate' option"
                        ).format(name)
                    )
                password = str(uuid.uuid4())
                service_uuid = self._create_service(name, password)
                self.app.file_manager.update(name, password)
            else:
                if not service_uuid:
                    raise RuntimeError(
                        (
                            "File exists but not the user ({}) associated. "
                            "Please use '--recreate' option"
                        ).format(name)
                    )

            self._create_or_update_service_policy(name, service_uuid, values['acl'])
            self.app.file_manager.update_ownership(name, values['system_user'])

    def _find_service_uuid(self, name):
        services = self.app.client.users.list(username=name)['items']
        for service in services:
            return service['uuid']

    def _delete_service(self, name):
        service_uuid = self._find_service_uuid(name)
        if not service_uuid:
            return

        self.app.client.users.delete(service_uuid)

    def _create_service(self, name, password):
        service = self.app.client.users.new(
            username=name, password=password, purpose='internal'
        )
        return service['uuid']

    def _find_policy(self, name):
        policies = self.app.client.policies.list(name=name)['items']
        for policy in policies:
            return policy

    def _delete_policy(self, username):
        name = POLICY_NAME_TPL.format(username=username)
        policy = self._find_policy(name)
        if not policy:
            return

        self.app.client.policies.delete(policy['uuid'])

    def _create_or_update_service_policy(self, username, service_uuid, acl):
        name = POLICY_NAME_TPL.format(username=username)
        policy = self._find_policy(name)
        if not policy:
            policy = self.app.client.policies.new(name, acl_templates=acl)
            self.app.client.users.add_policy(service_uuid, policy['uuid'])
            return

        if sorted(policy['acl_templates']) == sorted(acl):
            return
        self.app.client.policies.edit(policy['uuid'], name, acl_templates=acl)


class ServiceClean(Command):
    "Clean undefined files"

    def get_parser(self, *args, **kwargs):
        parser = super().get_parser(*args, **kwargs)
        parser.add_argument(
            '--users', help="Delete undefined internal users", action='store_true',
        )
        return parser

    def take_action(self, parsed_args):
        excludes = list(self.app.services.keys())
        if parsed_args.users:
            self.app.LOG.debug('Delete all undefined internal users')
            self._delete_services(excludes)

        self.app.file_manager.clean(excludes=excludes)

    def _delete_services(self, excludes=None):
        excludes = excludes or []
        excludes.append('wazo-auth-cli')
        services = self.app.client.users.list(purpose='internal')['items']
        for service in services:
            if service['username'] in excludes:
                continue

            policies = self.app.client.users.get_policies(service['uuid'])['items']
            for policy in policies:
                self.app.LOG.debug('Deleting policy: %s', policy['name'])
                self.app.client.policies.delete(policy['uuid'])
            self.app.LOG.debug('Deleting user: %s', service['username'])
            self.app.client.users.delete(service['uuid'])
