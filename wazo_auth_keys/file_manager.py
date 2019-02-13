# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import pwd
import yaml

DONT_CHANGE = -1
FILENAME_TPL = '{service_id}-key.yml'


class FileManager:

    def __init__(self, app, base_dir):
        self.app = app
        self._base_dir = base_dir
        self._full_path_tpl = os.path.join(self._base_dir, FILENAME_TPL)
        self._system_user_map = {pw.pw_name: pw.pw_uid for pw in pwd.getpwall()}

    def update(self, service_id, service_key):
        full_path = self._full_path_tpl.format(service_id=service_id)
        self._write_config_file(full_path, service_id, service_key)

    def remove(self, service_id):
        full_path = self._full_path_tpl.format(service_id=service_id)
        try:
            os.remove(full_path)
        except OSError:
            self.app.LOG.debug('File does not exist: %s', full_path)

    def update_ownership(self, service_id, system_user):
        full_path = self._full_path_tpl.format(service_id=service_id)
        uid = self._system_user_map.get(system_user, DONT_CHANGE)
        self.app.LOG.debug('Changing ownership %s ...', full_path)
        os.chown(full_path, uid, DONT_CHANGE)
        os.chmod(full_path, 0o600)

    def _write_config_file(self, full_path, service_id, service_key):
        self.app.LOG.debug('Writing %s ...', full_path)
        os.mknod(full_path)
        os.chmod(full_path, 0o600)
        with open(full_path, 'w') as fobj:
            yaml.safe_dump({'service_id': service_id, 'service_key': service_key}, fobj)

    def service_exists(self, service_id):
        search = FILENAME_TPL.format(service_id=service_id)
        filenames = os.listdir(self._base_dir)
        if search in filenames:
            return True
        return False

    def clean(self, excludes=None):
        excludes = excludes or []
        directory_filenames = os.listdir(self._base_dir)
        exclude_filenames = [FILENAME_TPL.format(service_id=service_id) for service_id in excludes]
        for filename in directory_filenames:
            if filename in exclude_filenames:
                continue
            full_path = os.path.join(self._base_dir, filename)
            self.app.LOG.debug('Removing %s ...', full_path)
            os.remove(full_path)
