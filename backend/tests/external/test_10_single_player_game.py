import uuid

import requests

from tests.external.utils import create_headers


def test_sp_game_create(smear_host, state):
    url = f"{smear_host}/api/smear/v1/games/"
    game_data = {
        'name': f'test_game_{str(uuid.uuid4())[:8]}',
        'passcode': '',
        'num_players': 4,
        'num_teams': 2,
        'score_to_play_to': 11,
        'single_player': True,
    }

    response = requests.post(url, json=game_data, headers=create_headers(state['user']['token']))

    assert response.status_code == 201, response.text
    state['sp_game'] = response.json()
