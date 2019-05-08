# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from cliff.command import Command


class PolicyUpdate(Command):
    "Update or create all policies defined in the config file"

    def get_parser(self, *args, **kwargs):
        parser = super().get_parser(*args, **kwargs)
        parser.add_argument(
            '--recreate',
            help="Delete policy before updating it",
            action='store_true',
        )
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.debug('Parsed args: %s', parsed_args)

        for name, acl in self.app.policies.items():
            if parsed_args.recreate:
                self._delete_policy(name)

            self._create_or_update_policy(name, acl)

    def _find_policy(self, name):
        policies = self.app.client.policies.list(name=name)['items']
        for policy in policies:
            return policy

    def _delete_policy(self, name):
        policy = self._find_policy(name)
        if not policy:
            return

        self.app.client.policies.delete(policy['uuid'])

    def _create_or_update_policy(self, name, acl):
        policy = self._find_policy(name)
        if not policy:
            self.app.client.policies.new(name, acl_templates=acl)
            return

        if sorted(policy['acl_templates']) == sorted(acl):
            return
        self.app.client.policies.edit(policy['uuid'], name, acl_templates=acl)
