#!/usr/bin/env python

"""Tests for `stateless_client` package."""


import unittest

from stateless_client.client import StatelessClient


class TestStateless_client(unittest.TestCase):
    """Tests for `stateless_client` package."""

    def setUp(self):
        self.test_scope = StatelessClient('https://foo:password@aion-dev.herokuapp.com/testProject', 'testScope')

    def tearDown(self):
        pass

    def test_get_current_state(self):
        data = self.test_scope.get
        data['foo'] = 'baz'
        self.test_scope.set(data)

        self.test_scope.checkout()
        print(self.test_scope.get)
        print(self.test_scope.getFullScope)
        pass

