#!/usr/bin/env python

"""Tests for `aion_client` package."""


import unittest

from aion_client.client import AionClient


class Testaion_client(unittest.TestCase):
    """Tests for `aion_client` package."""

    def setUp(self):
        self.test_client = AionClient('https://foo:password@aion-dev.herokuapp.com/testProject2')
        self.stateless = self.test_client.get_stateless_client('test_scope')
        self.queue = self.test_client.get_queue_client('test_queue')

    def tearDown(self):
        pass

    def test_get_current_state(self):
        data = self.stateless.get
        data['foo'] = 'baz'
        self.stateless.set(data)

        self.stateless.checkout()
        print(self.stateless.get)
        print(self.stateless.get_full_scope)
        pass

    def test_queueing(self):
        self.queue.publish({'weather': 'sunny'})
        self.queue.publish({'weather': 'sunny'})
        item = self.queue.fetch()
        print(item.id)
        print(item.data)
        item.complete()

