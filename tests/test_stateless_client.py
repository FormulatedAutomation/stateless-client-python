#!/usr/bin/env python

"""Tests for `stateless_client` package."""


import unittest

from stateless_client.client import StatelessClient


class TestStateless_client(unittest.TestCase):
    """Tests for `stateless_client` package."""

    def setUp(self):
        self.test_scope = StatelessClient('testProject', 'testScope')

    def tearDown(self):
        pass

    def test_get_current_state(self):
        pass

