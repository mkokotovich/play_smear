from unittest.mock import ANY

import requests

from tests.external.test_20_multi_player_game_setup import get_game
from tests.external.utils import create_headers


def add_player_to_team(smear_host, user, game, team, player):
    url = f"{smear_host}/api/smear/v1/games/{game['id']}/teams/{team['id']}/member/"
    data = {
        "id": player["id"],
    }

    response = requests.post(url, json=data, headers=create_headers(user["token"]))

    assert response.status_code == 200, response.text
    response_json = response.json()
    members = response_json.pop("members")
    assert len(members) > 0
    assert response_json == {
        "id": team["id"],
        "name": team["name"],
        "score": 0,
        "winner": False,
        "color": ANY,
    }

    return response.json()


def test_mp_game_add_players_to_teams(smear_host, state):
    # First, refresh our view of the game
    state["mp_game"] = get_game(smear_host, state["mp_game"]["id"], state["user"])

    num_teams = state["mp_game"]["num_teams"]
    for player_num, player in enumerate(state["mp_game"]["players"]):
        team = state["mp_game"]["teams"][player_num % num_teams]
        add_player_to_team(smear_host, state["user"], state["mp_game"], team, player)


def rename_team(smear_host, user, game, team, new_name):
    url = f"{smear_host}/api/smear/v1/games/{game['id']}/teams/{team['id']}/"
    data = {"name": new_name}

    response = requests.patch(url, json=data, headers=create_headers(user["token"]))
    return response


def test_mp_game_team_rename(smear_host, state):
    # First, refresh our view of the game
    state["mp_game"] = get_game(smear_host, state["mp_game"]["id"], state["user"])

    # Then try renaming a team the user isn't on. This should fail
    user2_team_id = next(
        player["team"] for player in state["mp_game"]["players"] if player["user"] == state["user2"]["id"]
    )
    not_user2_team = next(team for team in state["mp_game"]["teams"] if team["id"] != user2_team_id)
    response = rename_team(smear_host, state["user2"], state["mp_game"], not_user2_team, "coolname")
    assert response.status_code == 403

    # Then rename the team the user belongs to
    user2_team = next(team for team in state["mp_game"]["teams"] if team["id"] == user2_team_id)
    response = rename_team(smear_host, state["user2"], state["mp_game"], user2_team, "coolname")
    assert response.status_code == 200

    # And verify the team has a new name
    url = f"{smear_host}/api/smear/v1/games/{state['mp_game']['id']}/teams/{user2_team['id']}/"
    response = requests.get(url, headers=create_headers(state["user"]["token"]))
    assert response.status_code == 200
    assert response.json() == {
        "id": user2_team["id"],
        "name": "coolname",
        "score": 0,
        "winner": False,
        "color": ANY,
    }


def reset_team(smear_host, user, game):
    url = f"{smear_host}/api/smear/v1/games/{game['id']}/teams/all/"

    response = requests.delete(url, headers=create_headers(user["token"]))
    return response


def autofill_team(smear_host, user, game):
    url = f"{smear_host}/api/smear/v1/games/{game['id']}/teams/all/"

    response = requests.post(url, headers=create_headers(user["token"]))
    return response


def test_mp_game_team_reset_and_autofill(smear_host, state):
    response = reset_team(smear_host, state["user"], state["mp_game"])
    assert response.status_code == 200, response.text

    response = autofill_team(smear_host, state["user"], state["mp_game"])
    assert response.status_code == 200, response.text
