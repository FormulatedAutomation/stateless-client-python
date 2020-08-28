from urllib.parse import urlparse

from aion_client.stateless_client import StatelessClient
from aion_client.job_client import JobClient

class AionClient:

    def __init__(self, api_uri):
        u = urlparse(api_uri)
        self.api_url = f'https://{u.hostname}'
        self.project_id = u.path[1:]
    
    def get_stateless_client(self, scope):
        return StatelessClient(self.api_url, self.project_id, scope)

    def get_job_client(self, queue_name):
        return JobClient(self.api_url, self.project_id, queue_name)
