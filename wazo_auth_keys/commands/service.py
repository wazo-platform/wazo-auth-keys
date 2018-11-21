# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import uuid

from cliff.command import Command

POLICY_NAME_TPL = '{username}-internal'


class ServiceUpdate(Command):
    "Update or create all users defined in the config file"

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

        for name, values in self.app.services.items():
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
        services = self.app.client.users.list(username=name)['items']
        self.app.LOG.debug(services)
        if not services:
            return
        return services[0]['uuid']

    def _delete_service(self, name):
        service_uuid = self._get_service_uuid(name)
        if not service_uuid:
            return

        self.app.client.users.delete(service_uuid)

    def _create_service(self, name, password):
        service = self.app.client.users.new(username=name, password=password, purpose='internal')
        return service['uuid']

    def _get_policy_uuid(self, name):
        policies = self.app.client.policies.list(name=name)['items']
        if not policies:
            return
        return policies[0]['uuid']

    def _delete_service_policy(self, username):
        name = POLICY_NAME_TPL.format(username=username)
        policy_uuid = self._get_policy_uuid(name)
        if not policy_uuid:
            return

        self.app.client.policies.delete(policy_uuid)

    def _create_service_policy(self, username, service_uuid, acl):
        name = POLICY_NAME_TPL.format(username=username)
        policy = self.app.client.policies.new(name, acl_templates=acl)
        self.app.client.users.add_policy(service_uuid, policy['uuid'])


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

        self.app.file_manager.clean(excludes=list(self.app.services.keys()))
