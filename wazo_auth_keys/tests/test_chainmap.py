# Copyright 2020 The Wazo Authors
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from ..config_helper import ChainMap


class TestChainMap(unittest.TestCase):
    def test_chain_map_merge_dict(self):
        chain_map = ChainMap(
            {"key1": "value", "mydict": {"a": "b"}},
            {"mydict": {"c": "d"}},
        )

        self.assertEqual(chain_map, {'key1': 'value', 'mydict': {'a': 'b', "c": "d"}})

    def test_chain_map_merge_list(self):
        chain_map = ChainMap(
            {"key1": "value", "mylist": ["a", "b"]},
            {"mylist": ["c"]},
        )

        self.assertEqual(chain_map, {'key1': 'value', 'mylist': ['a', 'b', 'c']})

    def test_chain_map_dont_override_list(self):
        chain_map = ChainMap(
            {"key1": "value", "mylist": ["a", "b"]},
            {"mylist": "c"},
        )

        self.assertEqual(chain_map, {'key1': 'value', 'mylist': ['a', 'b']})