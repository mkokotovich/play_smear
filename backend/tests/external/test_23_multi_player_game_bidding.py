from tests.external.utils import update_game


def test_mp_game_returns_cards(smear_host, state):
    response = update_game(smear_host, state, 'mp_game')
    assert response.status_code == 200, response.text

    assert len(state['mp_game']['current_hand']['cards']) == 6
