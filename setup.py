#!/usr/bin/env python3
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import setup
from setuptools import find_packages


setup(
    name='wazo-auth-keys',
    version='1.0',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo.community',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'wazo-auth-keys = wazo_auth_keys.main:main',
        ],
        'wazo_auth_keys.commands': [
            'service_update = wazo_auth_keys.commands.service:ServiceUpdate',
            'service_clean = wazo_auth_keys.commands.service:ServiceClean',
        ],
    },
)
