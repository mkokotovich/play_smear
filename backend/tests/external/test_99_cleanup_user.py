import requests

from tests.external.utils import create_headers


def delete_user(smear_host, user):
    url = f"{smear_host}/api/users/v1/{user['id']}/"

    response = requests.delete(url, headers=create_headers(user['token']))

    assert response.status_code == 204, response.text


def test_user_delete(smear_host, state):
    delete_user(smear_host, state['user'])
    del state['user']


def test_user2_delete(smear_host, state):
    delete_user(smear_host, state['user2'])
    del state['user2']
