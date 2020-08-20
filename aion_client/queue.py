import requests
import json
from datetime import datetime, timedelta, date

from aion_client.exceptions import AionNetworkException
from aion_client.queue_item import QueueItem
from aion_client.datetime_json_encoder import DateTimeEncoder


class Queue:

    def __init__(self, api_url, project_id):
        self.project_id = project_id
        self.api_url = api_url

    def publish(self, queue_name, value):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        try:
            postData = {
                'data': value
            }
            r = requests.post(f"{self.api_url}/api/queue/publish/{self.project_id}/{queue_name}",
            data=json.dumps(postData, cls=DateTimeEncoder),
            headers=headers)
        except requests.exceptions.HTTPError:
            raise AionQueueNetworkException
        response_json = r.json()
        return response_json

    # Returns one item from the queue
    def fetch(self, queue_name):
        try:
            r = requests.get(f"{self.api_url}/api/queue/fetch/{self.project_id}/{queue_name}")
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise AionQueueNetworkException
        if r.json():
            return QueueItem(r.json(), self)
        return None

    def complete(self, id):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        try:
            r = requests.post(f"{self.api_url}/api/queue/complete/{id}",
            headers=headers)
        except requests.exceptions.HTTPError:
            raise AionQueueNetworkException
        response_json = r.json()
        if not response_json.get('committed'):
            raise AionQueueNotCommittedException
        return response_json

    def fail(self, id):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        try:
            r = requests.post(f"{self.api_url}/api/queue/fail/{id}",
            headers=headers)
        except requests.exceptions.HTTPError:
            raise AionQueueNetworkException
        response_json = r.json()
        if not response_json['committed']:
            raise AionQueueNotCommittedException
        return response_json