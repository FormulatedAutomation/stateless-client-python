import requests

STATE = {
    "started": "Started",
    "checked_out": "Checked Out",
    "committed": "Committed",
}

from aion_client.exceptions import StatelessNetworkException, StatelessNotCommittedException, \
    StatelessNotCheckedOutException, StatelessBadStateChange

class Stateless:

    def __init__(self, api_url, project_id, scope, checkout_state_on_init=True):
        self.api_url = api_url
        self.project_id = project_id
        self.scope = scope
        self.change_ids = list()
        self._data = None
        self.committed = False
        self.state = STATE['started']
        if checkout_state_on_init:
            self.checkout()
        return None

    def checkout(self):
        self._checkout_state()
        self._change_state(STATE['checked_out'])
        self.committed = False
        return self._data[self.scope]

    @property
    def get(self, default=None):
        if not self.state == STATE['checked_out']:
            raise StatelessNotCheckedOutException
        return self._data.get(self.scope, default)

    @property
    def getFullScope(self):
        if not self.state == STATE['checked_out']:
            raise StatelessNotCheckedOutException
        return self._data

    def set(self, value):
        if self.state == STATE['committed']:
            raise StatelessAlreadyCommittedException
        try:
            r = requests.post(f"{self.api_url}/api/state/commit/{self._current_change_id}/{self.scope}", json=value)
        except requests.exceptions.HTTPError:
            raise StatelessNetworkException
        response_json = r.json()
        if not response_json['committed']:
            raise StatelessNotCommittedException
        self._change_state(STATE['committed'])
        self.committed = True

    @property
    def _current_change_id(self):
        try:
            current_change_id = self.change_ids[0]
        except IndexError:
            raise StatelessNotCheckedOutException
        return current_change_id

    def _checkout_state(self):
        try:
            r = requests.get(f"{self.api_url}/api/state/checkout/{self.project_id}/{self.scope}")
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

    def _change_state(self, new_state):
        if self.state == STATE['started']:
            if not new_state == STATE['checked_out']:
                raise StatelessBadStateChange(f'Can\'t change from Started to {new_state}')
        elif self.state == STATE['checked_out']:
            if not new_state == STATE['committed']:
                raise StatelessBadStateChange(f'Can\'t change from \'Checked Out\' to {new_state}')
        elif not new_state == STATE['checked_out']:
                raise StatelessBadStateChange(f'Can\'t make changes after a Commit')
        self.state = new_state
