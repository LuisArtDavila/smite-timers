import re
import json
import typing
import requests
from hashlib import md5
from datetime import datetime
from sys import version_info

BASE_ENDPOINT = 'https://api.smitegame.com/smiteapi.svc'
DEV_ID = 0000
AUTH_KEY = 'YOUR_AUTH_KEY_HERE'


class HiRezAPI:
    def __init__(self, dev_id, auth_key, endpoint, **kwargs):
        self.auth_key = auth_key
        self.dev_id = dev_id
        self.endpoint = endpoint
        self.session_id = None

        self.headers = kwargs.pop('headers', {})

        if 'user-agent' not in self.headers:
            self.headers['user-agent'] = f'HiRezAPIWrapper [Python/{version_info.major}.{version_info.minor}]'

    def request(self, method, language_code: typing.Optional[int] = None, **headers) -> typing.Any:
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        signature = md5(f'{self.dev_id}{method.lower()}{self.auth_key}{timestamp}'.encode('utf-8')).hexdigest()
        endpoint = f'{self.endpoint}/{method}json/{self.dev_id}/{signature}'

        if self.session_id:
            endpoint = f'{endpoint}/{self.session_id}'

        endpoint = f'{endpoint}/{timestamp}'

        if language_code:
            endpoint = f'{endpoint}/{language_code}'

        response = requests.get(url=endpoint, headers={**self.headers, **headers})

        if response.headers.get('Content-Type').startswith('application/json'):
            return response.json()

        return response.text

    def create_session(self):
        response = self.request('createsession')

        assert response['ret_msg'].lower() == 'approved'

        try:
            self.session_id = response['session_id']
            print(f'Got session ID: {self.session_id}')
        except KeyError:
            print('Unable to get a session id.')

    def get_items(self):
        response = self.request('getitems', language_code=1)

        return response

    def get_relic_cooldowns(self):
        cooldown_regexpr = re.compile(r'Cooldown - (\d*)s.')
        items: typing.List[dict] = self.get_items()
        relic_cooldowns = {}

        for item in items:
            if item['ActiveFlag'].lower() == 'n':
                # Skip disabled items
                continue

            # Items that are "Active" types are relics.
            if item['Type'].lower() == 'active':
                relic_name = item['DeviceName']
                relic_desc = item['ItemDescription']['SecondaryDescription']

                cooldown_search = cooldown_regexpr.search(relic_desc)
                try:
                    cooldown_in_seconds = cooldown_search.group(1)
                    cooldown_in_seconds = int(cooldown_in_seconds)
                    minutes, seconds = divmod(cooldown_in_seconds, 60)

                    # print(f'{relic_name} has a cooldown of {minutes} minutes and {seconds} seconds.')

                    relic_cooldowns[relic_name] = (minutes, seconds)
                except AttributeError:
                    pass  # First relic.

        return relic_cooldowns

    def get_gods(self):
        response = self.request('getgods', language_code=1)

        gods = {}

        for god in response:
            god_name = god['Name']
            god_role = god['Roles']

            gods[god_name] = god_role

        return gods


hirez_api = HiRezAPI(
    dev_id=DEV_ID,
    auth_key=AUTH_KEY,
    endpoint=BASE_ENDPOINT
)
hirez_api.create_session()
relic_cooldowns = hirez_api.get_relic_cooldowns()

with open('relics.json', 'w') as relics_file:
    json.dump(relic_cooldowns, relics_file, indent=2)

gods = hirez_api.get_gods()

with open('gods.json', 'w') as gods_file:
    json.dump(gods, gods_file, indent=2)

