import requests

from tests.external.utils import create_headers


def test_mp_game_delete(smear_host, state):
    url = f"{smear_host}/api/smear/v1/games/{state['mp_game']['id']}/"

    response = requests.delete(url, headers=create_headers(state['user']['token']))

    assert response.status_code == 204, response.text
    del state['mp_game']
