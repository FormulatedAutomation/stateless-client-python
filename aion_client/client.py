from urllib.parse import urlparse

from aion_client.stateless import Stateless
from aion_client.queue import Queue

class AionClient:

    def __init__(self, api_uri, scope, checkout_state_on_init=True):
        u = urlparse(api_uri)
        self.api_url = f'https://{u.hostname}'
        self.project_id = u.path[1:]
        self.scope = scope
        self.stateless = Stateless(self.api_url, self.project_id, self.scope)
        self.queue = Queue(self.api_url, self.project_id)
