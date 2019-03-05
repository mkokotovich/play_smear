import requests


def create_headers(token):
    return {'Authorization': f"Bearer {token}"}


def update_game(smear_host, state, game, user='user'):
    url = f"{smear_host}/api/smear/v1/games/{state[game]['id']}/"

    response = requests.get(url, headers=create_headers(state[user]['token']))

    if response.status_code == 200:
        state[game] = {
            **state[game],
            **response.json(),
        }

    return response


def update_status(smear_host, state, game, user='user'):
    url = f"{smear_host}/api/smear/v1/games/{state[game]['id']}/status/"

    response = requests.get(url, headers=create_headers(state[user]['token']))

    if response.status_code == 200:
        state[game] = {
            **state[game],
            **response.json(),
        }

    return response


def submit_bid(smear_host, state, game, user, bid):
    url = f"{smear_host}/api/smear/v1/games/{state[game]['id']}/bids/"
    data = {'bid': bid}

    response = requests.post(url, headers=create_headers(state[user]['token']), json=data)

    return response
