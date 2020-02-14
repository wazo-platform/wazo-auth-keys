# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from copy import copy

from xivo.chain_map import ChainMap as _ChainMap
from xivo.config_helper import ConfigParser as _ConfigParser


class ConfigParser(_ConfigParser):

    def read_config_file_hierarchy(self, original_config):

        main_config_filename = original_config['config_file']
        main_config = self.parse_config_file(main_config_filename)
        extra_config_file_directory = ChainMap(main_config, original_config)['extra_config_files']
        configs = self.parse_config_dir(extra_config_file_directory)
        configs.append(main_config)

        return ChainMap(*configs)


class ChainMap(_ChainMap):

    def _deep_update(self, original, new):
        updated = copy(original)

        for key, value in new.items():
            if key not in updated:
                updated[key] = copy(value)
            elif isinstance(updated[key], dict) and isinstance(value, dict):
                updated[key] = self._deep_update(updated[key], value)
            elif isinstance(updated[key], list) and isinstance(value, list):
                updated[key].extend(copy(value))

        return updated


read_config_file_hierarchy = ConfigParser().read_config_file_hierarchy
