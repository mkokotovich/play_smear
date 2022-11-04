import requests


def get_token(smear_host, user):
    url = f"{smear_host}/api/auth/"
    body = {
        "username": user["username"],
        "password": user["password"],
    }

    response = requests.post(url, json=body)

    assert response.status_code == 201, response.text
    assert response.json()["user"] == {
        "id": user["id"],
        "username": user["username"],
    }
    user["token"] = response.json()["token"]


def test_auth_get_token(smear_host, state):
    get_token(smear_host, state["user"])


def test_auth_get_token_for_user2(smear_host, state):
    get_token(smear_host, state["user2"])
