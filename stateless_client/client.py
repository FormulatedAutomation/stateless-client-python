import requests

from stateless_client.exceptions import StatelessNetworkException, StatelessNotCommittedException, \
    StatelessNotInitedException


class StatelessClient:

    def __init__(self, project_key, scope):
        self.project_key = project_key
        self.scope = scope
        self.api_url = "https://hidden-stream-66951.herokuapp.com"
        self.change_ids = list()
        self._data = None
        self._get_initial_data()

    def get(self, key, default=None, *args, **kwargs):
        self._get_initial_data()
        return self._data.get(key, default)

    def set(self, key, value):
        try:
            r = requests.post(f"{self.api_url}/api/state/commit/{self._current_change_id}/{self.scope}", json=value)
        except requests.exceptions.HTTPError:
            raise StatelessNetworkException
        response_json = r.json()
        if not response_json['committed']:
            raise StatelessNotCommittedException
        self._get_initial_data()

    @property
    def _current_change_id(self):
        try:
            current_change_id = self.change_ids[0]
        except IndexError:
            raise StatelessNotInitedException
        return current_change_id

    def _get_initial_data(self):
        try:
            r = requests.get(f"{self.api_url}/api/state/checkout/{self.project_key}/{self.scope}")
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise StatelessNetworkException
        response_json = r.json()
        current_data = response_json['state']['data']
        self._set_change_id(response_json['changeId'])
        self._set_data(current_data)

    def _set_change_id(self, change_id):
        self.change_ids.insert(0, change_id)

    def _set_data(self, data):
        self._data = data
