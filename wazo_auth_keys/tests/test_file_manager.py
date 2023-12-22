# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os.path as os_path
from unittest import TestCase
from unittest.mock import Mock, patch

from ..file_manager import FileManager


@patch('wazo_auth_keys.file_manager.os')
class TestFileManager(TestCase):
    def setUp(self):
        app = Mock()
        base_dir = '/base'
        self.file_manager = FileManager(app, base_dir)

    def test_clean_empty(self, os):
        os.listdir.return_value = []

        self.file_manager.clean()

    def test_clean_two_files(self, os):
        os.listdir.return_value = ['a', 'b']
        os.path.join = os_path.join

        self.file_manager.clean()

        os.remove.assert_any_call('/base/a')
        os.remove.assert_any_call('/base/b')

    def test_clean_excluded(self, os):
        os.listdir.return_value = ['a', 'b', 'bb', 'c']
        os.path.join = os_path.join
        excludes = 'b'

        self.file_manager.clean(excludes)

        os.remove.assert_any_call('/base/a')
        os.remove.assert_any_call('/base/bb')
        os.remove.assert_any_call('/base/c')
