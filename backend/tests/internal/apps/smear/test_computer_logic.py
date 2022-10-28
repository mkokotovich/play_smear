import pytest

from apps.smear.computer_logic import calculate_bid
from tests.internal.apps.smear.factories import HandFactory, PlayerFactory


@pytest.mark.django_db
@pytest.mark.parametrize("num_players", (2, 3, 4, 8))
def test_calculate_bid_ace_jack(mocker, num_players):
    card_reps = ["AS", "JS", "3H", "4H", "3D", "4D"]

    mock_hand = HandFactory(game__num_players=num_players)
    mock_player = PlayerFactory(game=mock_hand.game, cards_in_hand=card_reps)

    bid_value, trump_value = calculate_bid(mock_player, mock_hand)

    assert bid_value == 2


@pytest.mark.django_db
@pytest.mark.parametrize("num_players", (2, 3, 4, 8))
def test_calculate_bid_jack_duece(mocker, num_players):
    card_reps = ["JS", "2S", "3H", "4H", "3D", "4D"]

    mock_hand = HandFactory(game__num_players=num_players)
    mock_player = PlayerFactory(game=mock_hand.game, cards_in_hand=card_reps)

    bid_value, trump_value = calculate_bid(mock_player, mock_hand)

    match num_players:
        case 2:
            expected_bid = 3
        case 3:
            expected_bid = 2
        case 4:
            expected_bid = 0
        case 8:
            expected_bid = 0

    assert bid_value == expected_bid


@pytest.mark.django_db
@pytest.mark.parametrize("num_players", (2, 3, 4, 8))
def test_calculate_bid_ace_duece(mocker, num_players):
    card_reps = ["AS", "2S", "3H", "4H", "3D", "4D"]

    mock_hand = HandFactory(game__num_players=num_players)
    mock_player = PlayerFactory(game=mock_hand.game, cards_in_hand=card_reps)

    bid_value, trump_value = calculate_bid(mock_player, mock_hand)

    match num_players:
        case 2:
            expected_bid = 2
        case 3:
            expected_bid = 2
        case 4:
            expected_bid = 2
        case 8:
            expected_bid = 2

    assert bid_value == expected_bid


@pytest.mark.django_db
@pytest.mark.parametrize("num_players", (2, 3, 4, 8))
def test_calculate_bid_ace_king(mocker, num_players):
    card_reps = ["AS", "KS", "3H", "4H", "3D", "4D"]

    mock_hand = HandFactory(game__num_players=num_players)
    mock_player = PlayerFactory(game=mock_hand.game, cards_in_hand=card_reps)

    bid_value, trump_value = calculate_bid(mock_player, mock_hand)

    match num_players:
        case 2:
            expected_bid = 0
        case 3:
            expected_bid = 2
        case 4:
            expected_bid = 2
        case 8:
            expected_bid = 2

    assert bid_value == expected_bid
