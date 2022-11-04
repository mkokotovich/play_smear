import uuid

import requests


def test_user_post(smear_host, state):
    url = f"{smear_host}/api/users/v1/"
    body = {
        "username": f"test_{str(uuid.uuid4())[:8]}@gmail.com",
        "password": "password",
    }

    response = requests.post(url, json=body)

    assert response.status_code == 201, response.text
    state["user"] = {
        **body,
        "id": response.json()["id"],
    }


def test_user2_post(smear_host, state):
    url = f"{smear_host}/api/users/v1/"
    body = {
        "username": f"test_{str(uuid.uuid4())[:8]}@gmail.com",
        "password": "password",
    }

    response = requests.post(url, json=body)

    assert response.status_code == 201, response.text
    state["user2"] = {
        **body,
        "id": response.json()["id"],
    }
