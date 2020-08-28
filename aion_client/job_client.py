import requests
import json

from aion_client.exceptions import AionNetworkException, AionNotCommittedException
from aion_client.datetime_json_encoder import DateTimeEncoder

class JobClient:
    def __init__(self, api_url, project_id, job_name):
        self.job = JobAPI(api_url, project_id)
        self.job_name = job_name

    def publish(self, value):
        return self.job.publish(self.job_name, value)

    def fetch(self, workerData={}):
        return self.job.fetch(self.job_name, workerData)

    def complete(self, id):
        return self.job.complete(id)

    def fail(self, id):
        return self.job.complete(id)

class JobItem:

    def __init__(self, q_item, q):
        self.job = q_item['job']
        self.work_ticket = q_item['workTicket']
        if (self.job):
            self._data = self.job['data']
        self.q = q

    @property
    def data(self):
        return self._data

    def get(self, key):
        return self._data[key]

    def complete(self, runData={}):
        self.q.complete(self.work_ticket['id'], runData)

    def fail(self, runData={}):
        self.q.fail(self.work_ticket['id'], runData)

class JobAPI:

    def __init__(self, api_url, project_id):
        self.project_id = project_id
        self.api_url = api_url

    def publish(self, job_name, value):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        try:
            postData = {
                'data': value
            }
            r = requests.post(f"{self.api_url}/api/job/publish/{self.project_id}/{job_name}",
            data=json.dumps(postData, cls=DateTimeEncoder),
            headers=headers)
        except requests.exceptions.HTTPError:
            raise AionNetworkException
        response_json = r.json()
        return response_json

    # Returns one item from the job
    def fetch(self, job_name, workerData={}):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        postData = {
            'workerData': workerData
        }
        try:
            r = requests.post(f"{self.api_url}/api/job/fetch/{self.project_id}/{job_name}",
            data=json.dumps(postData, cls=DateTimeEncoder),
            headers=headers)
            r.raise_for_status()
            result = r.json().get('result', None)
        except requests.exceptions.HTTPError:
            raise AionNetworkException
        if result and result['job']:
            return JobItem(result, self)
        return None

    def complete(self, id, runData={}):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        postData = {
            'runData': runData
        }
        try:
            r = requests.post(f"{self.api_url}/api/workTicket/{id}/complete",
            data=json.dumps(postData, cls=DateTimeEncoder),
            headers=headers)
        except requests.exceptions.HTTPError:
            raise AionNetworkException
        response_json = r.json()
        if not response_json.get('result'):
            raise AionNotCommittedException
        return response_json

    def fail(self, id, runData={}):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        postData = {
            'runData': runData
        }
        try:
            r = requests.post(f"{self.api_url}/api/workTicket/{id}/fail",
            data=json.dumps(postData, cls=DateTimeEncoder),
            headers=headers)
        except requests.exceptions.HTTPError:
            raise AionNetworkException
        response_json = r.json()
        if not response_json['result']:
            raise AionNotCommittedException
        return response_json