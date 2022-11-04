import requests

from tests.external.utils import create_headers


def test_user_list(smear_host, state):
    url = f"{smear_host}/api/users/v1/"

    response = requests.get(url, headers=create_headers(state["user"]["token"]))

    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json["count"] > 0
    assert "next" in response_json
    assert "previous" in response_json
    assert isinstance(response_json["results"], list)


def test_user_get(smear_host, state):
    url = f"{smear_host}/api/users/v1/{state['user']['id']}/"

    response = requests.get(url, headers=create_headers(state["user"]["token"]))

    assert response.status_code == 200, response.text
    assert response.json() == {
        "id": state["user"]["id"],
        "first_name": "",
        "last_name": "",
        "username": state["user"]["username"],
    }


# TODO: don't allow password changes on PUT
def test_user_put(smear_host, state):
    url = f"{smear_host}/api/users/v1/{state['user']['id']}/"

    response = requests.put(
        url,
        json={
            "first_name": "bob",
            "username": state["user"]["username"],
            "password": state["user"]["password"],
        },
        headers=create_headers(state["user"]["token"]),
    )

    assert response.status_code == 200, response.text
    assert response.json()["first_name"] == "bob"


def test_user_patch(smear_host, state):
    url = f"{smear_host}/api/users/v1/{state['user']['id']}/"

    response = requests.patch(url, json={"first_name": "first"}, headers=create_headers(state["user"]["token"]))

    assert response.status_code == 200, response.text
    assert response.json()["first_name"] == "first"
