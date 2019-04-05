# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from xivo.chain_map import ChainMap
from xivo.config_helper import parse_config_dir  # , read_config_file_hierarchy

from wazo_auth_cli.config import (
    _DEFAULT_CONFIG,
)

from .config_helper import read_config_file_hierarchy

SERVICES_CONFIG_FILE = 'config.yml'
SERVICES_EXTRA_CONFIG = 'conf.d'


def _read_user_config(parsed_args):
    if not parsed_args.wazo_auth_cli_config:
        return {}
    configs = parse_config_dir(parsed_args.wazo_auth_cli_config)
    return ChainMap(*configs)


def build(parsed_args):
    user_file_config = _read_user_config(parsed_args)
    system_file_config = read_config_file_hierarchy(ChainMap(user_file_config, _DEFAULT_CONFIG))
    final_config = ChainMap(user_file_config, system_file_config, _DEFAULT_CONFIG)
    return final_config


def load_services(parsed_args):
    services_dir = parsed_args.config
    services_config = {
        'config_file': os.path.join(services_dir, SERVICES_CONFIG_FILE),
        'extra_config_files': os.path.join(services_dir, SERVICES_EXTRA_CONFIG),
    }
    services = read_config_file_hierarchy(services_config)
    services.pop('config_file', None)
    services.pop('extra_config_files', None)
    return services
