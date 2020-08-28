#!/usr/bin/env python

"""Tests for `aion_client` package."""


import unittest
import re

from aion_client.client import AionClient


UUID_REGEX = re.compile("^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$", flags=re.IGNORECASE)


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
        self.assertEqual('baz', self.stateless.get['foo'])

    def test_job_queuing(self):
        item = self.job.fetch()
        self.job.publish({'weather': 'sunny'})
        self.job.publish({'weather': 'sunny'})
        item = self.job.fetch()
        self.assertIsNotNone(UUID_REGEX.match(item.work_ticket['id']))
        item.complete()

    def test_job_start(self):
        item = self.job.start({'botId': 'bot12345'})
        self.assertIsNotNone(UUID_REGEX.match(item.job['id']))
        self.assertIsNotNone(UUID_REGEX.match(item.work_ticket['id']))
        self.assertTrue(item.work_ticket['workerData']['botId'] == 'bot12345')
        item.complete()

