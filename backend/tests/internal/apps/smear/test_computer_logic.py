import pytest

from apps.smear.computer_logic import calculate_bid, choose_card
from apps.smear.models import Play
from tests.internal.apps.smear.factories import HandFactory, PlayerFactory, TrickFactory


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


@pytest.mark.django_db
@pytest.mark.parametrize("highest_trump", ("AS", "KS", "QS"))
def test_choose_card_lead_play_when_bidder_AKQ(mocker, highest_trump):
    card_reps = [highest_trump, "JS", "3H", "4H", "3D", "4D"]

    mock_trick = TrickFactory(
        hand__trump="spades",
    )
    mock_player = PlayerFactory(game=mock_trick.hand.game, cards_in_hand=card_reps)
    mock_trick.hand.bidder = mock_player

    card = choose_card(mock_player, mock_trick, current_plays_arg=None)

    assert card.representation == highest_trump


@pytest.mark.django_db
@pytest.mark.parametrize("spare", ("7S", "7H"))
def test_choose_card_lead_play_when_bidder_play_spare_trump(mocker, spare):
    card_reps = ["JS", "3S", spare, "0D", "0H"]

    mock_trick = TrickFactory(
        hand__trump="spades",
    )
    mock_player = PlayerFactory(game=mock_trick.hand.game, cards_in_hand=card_reps)
    mock_trick.hand.bidder = mock_player

    card = choose_card(mock_player, mock_trick, current_plays_arg=None)

    assert card.representation == ("3S" if spare == "7S" else "7H")


@pytest.mark.django_db
@pytest.mark.parametrize("face_card", ("AH", "KH", "QH", "JH"))
def test_choose_card_lead_play_choose_AKQJ_off_suit(mocker, face_card):
    card_reps = ["2H", "3H", "0D", face_card]

    mock_trick = TrickFactory(
        hand__trump="spades",
    )
    mock_player = PlayerFactory(game=mock_trick.hand.game, cards_in_hand=card_reps)
    mock_trick.hand.bidder = mock_player

    card = choose_card(mock_player, mock_trick, current_plays_arg=None)

    assert card.representation == face_card


@pytest.mark.django_db
def test_choose_card_lead_play_choose_non_10_off_suit(mocker):
    card_reps = ["2H", "7H", "0D"]

    mock_trick = TrickFactory(
        hand__trump="spades",
    )
    mock_player = PlayerFactory(game=mock_trick.hand.game, cards_in_hand=card_reps)
    mock_trick.hand.bidder = mock_player

    card = choose_card(mock_player, mock_trick, current_plays_arg=None)

    assert card.representation == "7H"


@pytest.mark.django_db
def test_choose_card_lead_play_choose_lowest_trump(mocker):
    card_reps = ["0S", "9S"]

    mock_trick = TrickFactory(
        hand__trump="spades",
    )
    mock_player = PlayerFactory(game=mock_trick.hand.game, cards_in_hand=card_reps)
    mock_trick.hand.bidder = mock_player

    card = choose_card(mock_player, mock_trick, current_plays_arg=None)

    assert card.representation == "9S"


@pytest.mark.django_db
def test_choose_card_lead_play_choose_anything(mocker):
    card_reps = ["0S"]

    mock_trick = TrickFactory(
        hand__trump="spades",
    )
    mock_player = PlayerFactory(game=mock_trick.hand.game, cards_in_hand=card_reps)
    mock_trick.hand.bidder = mock_player

    card = choose_card(mock_player, mock_trick, current_plays_arg=None)

    assert card.representation == "0S"


@pytest.mark.django_db
@pytest.mark.parametrize("jick_out", (True, False))
def test_choose_card_lead_jack_or_jick_if_they_are_high_trump_and_can_take_something_valuable_with_jack(
    mocker, jick_out
):
    card_reps = ["JS", "0S", "3H", "4H"]

    mock_trick = TrickFactory(
        hand__trump="spades",
        num=2,
    )
    earlier_trick = TrickFactory(hand=mock_trick.hand, num=1)

    Play.objects.create(trick=earlier_trick, card="AS")
    Play.objects.create(trick=earlier_trick, card="KS")
    Play.objects.create(trick=earlier_trick, card="QS")
    if not jick_out:
        Play.objects.create(trick=earlier_trick, card="JC")

    mock_player = PlayerFactory(game=mock_trick.hand.game, cards_in_hand=card_reps)
    mock_trick.active_player = mock_player

    plays = mock_trick.plays.all()

    card = choose_card(mock_player, mock_trick, plays)

    assert card.representation == ("JS" if jick_out else "4H")


@pytest.mark.django_db
@pytest.mark.parametrize("jack_out", (True, False))
def test_choose_card_lead_jack_or_jick_if_they_are_high_trump_and_can_take_something_valuable_with_jick(
    mocker, jack_out
):
    card_reps = ["JC", "2H", "3H", "4H"]

    mock_trick = TrickFactory(
        hand__trump="spades",
        num=2,
    )
    earlier_trick = TrickFactory(hand=mock_trick.hand, num=1)

    Play.objects.create(trick=earlier_trick, card="AS")
    Play.objects.create(trick=earlier_trick, card="KS")
    Play.objects.create(trick=earlier_trick, card="QS")
    if not jack_out:
        Play.objects.create(trick=earlier_trick, card="JS")

    mock_player = PlayerFactory(game=mock_trick.hand.game, cards_in_hand=card_reps)
    mock_trick.active_player = mock_player

    plays = mock_trick.plays.all()
    card = choose_card(mock_player, mock_trick, plays)

    # if jack is out, it could take our jick
    assert card.representation == ("4H" if jack_out else "JC")
