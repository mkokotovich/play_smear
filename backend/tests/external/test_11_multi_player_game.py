import uuid

import requests

from tests.external.utils import create_headers


def test_mp_game_create(smear_host, state):
    url = f"{smear_host}/api/smear/v1/games/"
    game_data = {
        'name': f'test_game_{str(uuid.uuid4())[:8]}',
        'passcode': 'passcode',
        'num_players': 4,
        'num_teams': 2,
        'score_to_play_to': 11,
        'single_player': False,
    }

    response = requests.post(url, json=game_data, headers=create_headers(state['user']['token']))

    assert response.status_code == 201, response.text
    state['mp_game'] = {
        **response.json(),
        'passcode': 'passcode',
    }


def test_mp_game_join(smear_host, state):
    url = f"{smear_host}/api/smear/v1/games/{state['mp_game']['id']}/join/"
    join_data = {
        'passcode': state['mp_game']['passcode'],
    }

    response = requests.post(url, json=join_data, headers=create_headers(state['user2']['token']))

    assert response.status_code == 200, response.text


def add_computer(smear_host, game, user):
    url = f"{smear_host}/api/smear/v1/games/{game['id']}/player/"

    response = requests.post(url, headers=create_headers(user['token']))

    assert response.status_code == 200, response.text

    return response.json()


def remove_player(smear_host, game, user, player_id):
    url = f"{smear_host}/api/smear/v1/games/{game['id']}/player/"
    player_data = {
        'id': player_id,
    }

    response = requests.delete(url, json=player_data, headers=create_headers(user['token']))

    assert response.status_code == 200, response.text


def test_mp_game_player(smear_host, state):
    player = add_computer(smear_host, state['mp_game'], state['user'])
    remove_player(smear_host, state['mp_game'], state['user'], player['id'])
    num_players = 2

    while num_players < state['mp_game']['num_players']:
        add_computer(smear_host, state['mp_game'], state['user'])
        num_players += 1
