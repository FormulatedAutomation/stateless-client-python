import requests
import json

from aion_client.exceptions import AionNetworkException, AionNotCommittedException
from aion_client.datetime_json_encoder import DateTimeEncoder

class QueueClient:
    def __init__(self, api_url, project_id, queue_name):
        self.queue = QueueAPI(api_url, project_id)
        self.queue_name = queue_name

    def publish(self, value):
        return self.queue.publish(self.queue_name, value)

    def fetch(self):
        return self.queue.fetch(self.queue_name)

    def complete(self, id):
        return self.queue.complete(id)

    def fail(self, id):
        return self.queue.complete(id)

class QueueItem:

    def __init__(self, q_item, q):
        self.id = q_item['id']
        self.data = q_item['data']
        self.q = q

    def complete(self):
        self.q.complete(self.id)

    def fail(self):
        self.q.fail(self.id)

class QueueAPI:

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
            raise AionNetworkException
        response_json = r.json()
        return response_json

    # Returns one item from the queue
    def fetch(self, queue_name):
        try:
            r = requests.get(f"{self.api_url}/api/queue/fetch/{self.project_id}/{queue_name}")
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise AionNetworkException
        if r.json():
            return QueueItem(r.json()['result'], self)
        return None

    def complete(self, id):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        try:
            r = requests.post(f"{self.api_url}/api/queue/complete/{id}",
            headers=headers)
        except requests.exceptions.HTTPError:
            raise AionNetworkException
        response_json = r.json()
        if not response_json.get('committed'):
            raise AionNotCommittedException
        return response_json

    def fail(self, id):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        try:
            r = requests.post(f"{self.api_url}/api/queue/fail/{id}",
            headers=headers)
        except requests.exceptions.HTTPError:
            raise AionNetworkException
        response_json = r.json()
        if not response_json['committed']:
            raise AionNotCommittedException
        return response_json