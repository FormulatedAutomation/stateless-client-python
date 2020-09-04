#!/usr/bin/env python

"""Tests for `aion_client` package."""

import unittest
import re
from unittest.mock import patch

from aion_client.client import AionClient

UUID_REGEX = re.compile("^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$", flags=re.IGNORECASE)


class TestAionClient(unittest.TestCase):
    """Tests for `aion_client` package."""

    def setUp(self):
        self.test_client = AionClient('https://foo:password@aion-dev.herokuapp.com/testProject2')
        self.job = self.test_client.get_job_client('test_queue2')

    def tearDown(self):
        pass

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

    @patch('aion_client.stateless_client.StatelessClient.fetch')
    def test_get_current_state(self, _checkout_state):
        _checkout_state.return_value = {
            'changeId': 'abc123',
            'state': {
                'id': 'testId',
                'projectId': 'testState',
                'version': '0',
                'data': {
                    'test_scope': {
                        'foo': 'bar'
                    }
                },
                'createdAt': '2020-08-11T21:28:32.527Z',
                'updatedAt': '2020-08-20T16:29:52.566Z'
            }
        }
        test_client = AionClient('https://foo:password@aion-dev.herokuapp.com/testProject')
        self.assertEqual(test_client.get_stateless_client('test_scope').get, {'foo': 'bar'})
