#!/usr/bin/env python

"""Tests for `aion_client` package."""


import unittest

from aion_client.client import AionClient


class Testaion_client(unittest.TestCase):
    """Tests for `aion_client` package."""

    def setUp(self):
        self.test_client = AionClient('https://foo:password@aion-dev.herokuapp.com/testProject2')
        self.stateless = self.test_client.get_stateless_client('test_scope')
        self.job = self.test_client.get_job_client('test_queue2')

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

    def test_job_queuing(self):
        item = self.job.fetch()
        print("Item")
        print(item)
        print("/Item")
        self.job.publish({'weather': 'sunny'})
        self.job.publish({'weather': 'sunny'})
        item = self.job.fetch()
        print(item.work_ticket['id'])
        print(item.data)
        item.complete()

