import requests

from tests.external.utils import create_headers, update_status


def start_game(smear_host, user, game):
    url = f"{smear_host}/api/smear/v1/games/{game['id']}/start/"

    response = requests.post(url, headers=create_headers(user['token']))
    return response


def test_mp_game_status(smear_host, state):
    response = update_status(smear_host, state, 'mp_game')
    assert response.status_code == 200, response.text


def test_mp_game_start(smear_host, state):
    # First try starting with a user who is not the game owner
    response = start_game(smear_host, state['user2'], state['mp_game'])
    assert response.status_code == 403, response.text

    # Then start it with the owner
    response = start_game(smear_host, state['user'], state['mp_game'])
    assert response.status_code == 200, response.text
