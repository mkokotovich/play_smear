import requests

from tests.external.utils import create_headers, update_game


def test_mp_game_returns_cards(smear_host, state):
    response = update_game(smear_host, state, "mp_game")
    assert response.status_code == 200, response.text
    assert response.json()["state"] == "bidding"

    assert len(state["mp_game"]["current_hand"]["cards"]) == 6


def test_mp_game_submit_bids_for_both_human_players(smear_host, state):
    print(state["mp_game"])
    url = (
        f"{smear_host}/api/smear/v1/games/{state['mp_game']['id']}/hands/{state['mp_game']['current_hand']['id']}/bids/"
    )
    bidder_player_id = state["mp_game"]["current_hand"]["bidder"]
    bidder_user_id = next(player["user"] for player in state["mp_game"]["players"] if player["id"] == bidder_player_id)
    first_bidder_token = state["user"]["token"] if state["user"]["id"] == bidder_user_id else state["user2"]["token"]
    second_bidder_token = state["user"]["token"] if state["user"]["id"] != bidder_user_id else state["user2"]["token"]

    bid_data = {
        "bid": 5,
    }
    response = requests.post(url, json=bid_data, headers=create_headers(first_bidder_token))
    assert response.status_code == 201, response.text

    bid_data = {
        "bid": 0,
    }
    response = requests.post(url, json=bid_data, headers=create_headers(second_bidder_token))
    assert response.status_code == 201, response.text
