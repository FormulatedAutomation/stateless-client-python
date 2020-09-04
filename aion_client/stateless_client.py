import requests

from aion_client.exceptions import StatelessNetworkException, StatelessNotCommittedException, \
    StatelessNotCheckedOutException, StatelessBadStateChange, StatelessAlreadyCommittedException

STARTED = 'started'
CHECKED_OUT = 'checked_out'
COMMITTED = 'committed'

STATE = (
    (STARTED, 'Started'),
    (CHECKED_OUT, 'Checked Out'),
    (COMMITTED, 'Committed'),
)


class StatelessClient:

    def __init__(self, api_url, project_id, scope, checkout_state_on_init=True):
        self.api_url = api_url
        self.project_id = project_id
        self.scope = scope
        self.change_ids = list()
        self._data = None
        self.committed = False
        self.state = STARTED
        if checkout_state_on_init:
            self.checkout()

    def checkout(self):
        self._checkout_state()
        self._change_state(CHECKED_OUT)
        self.committed = False
        if self.scope in self._data:
            return self._data[self.scope]
        return {}

    @property
    def get(self, default=None):
        if not self.state == CHECKED_OUT:
            raise StatelessNotCheckedOutException
        return self._data.get(self.scope, default)

    @property
    def get_full_scope(self):
        if not self.state == CHECKED_OUT:
            raise StatelessNotCheckedOutException
        return self._data

    def set(self, value):
        print(self.scope)
        print(value)
        if self.state == COMMITTED:
            raise StatelessAlreadyCommittedException
        try:
            r = requests.post(f"{self.api_url}/api/state/commit/{self._current_change_id}/{self.scope}", json=value)
        except requests.exceptions.HTTPError:
            raise StatelessNetworkException
        response_json = r.json()
        if not COMMITTED:
            raise StatelessNotCommittedException
        self._change_state(COMMITTED)
        self.committed = True

    @property
    def _current_change_id(self):
        try:
            current_change_id = self.change_ids[0]
        except IndexError:
            raise StatelessNotCheckedOutException
        return current_change_id

    def _checkout_state(self):
        response_json = self.fetch()
        current_data = response_json['state']['data']
        self._set_change_id(response_json['changeId'])
        print(current_data)
        self._set_data(current_data)

    def fetch(self):
        try:
            r = requests.get(f"{self.api_url}/api/state/checkout/{self.project_id}/{self.scope}")
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise StatelessNetworkException
        return r.json()

    def _set_change_id(self, change_id):
        self.change_ids.insert(0, change_id)

    def _set_data(self, data):
        self._data = data

    def _change_state(self, new_state):
        if self.state == STARTED:
            if not new_state == CHECKED_OUT:
                raise StatelessBadStateChange(f'Can\'t change from Started to {new_state}')
        elif self.state == CHECKED_OUT:
            if not new_state == COMMITTED:
                raise StatelessBadStateChange(f'Can\'t change from \'Checked Out\' to {new_state}')
        elif not new_state == CHECKED_OUT:
            raise StatelessBadStateChange(f'Can\'t make changes after a Commit')
        self.state = new_state
