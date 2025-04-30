import pytest

from apps.smear.cards import Card
from apps.smear.models import Play
from tests.internal.apps.smear.factories import GameFactory, PlayerFactory, TrickFactory


@pytest.mark.django_db
def test_update_if_out_of_cards_did_not_follow_trump():
    game = GameFactory(num_players=3, num_teams=0)
    p1 = PlayerFactory(user=game.owner, game=game, seat=1)
    p2 = PlayerFactory(game=game, seat=2)
    PlayerFactory(game=game, seat=3)
    game.set_plays_after()

    trick = TrickFactory(hand__game=game, hand__trump="hearts")

    lead_play = Play.objects.create(trick=trick, card="AH", player=p1)
    Play.objects.create(trick=trick, card="2S", player=p2)

    trick.hand.update_if_out_of_cards(p2, Card(representation="2S"), lead_play)

    assert trick.hand.players_out_of_suits["hearts"] == [str(p2.id)]


@pytest.mark.django_db
def test_is_card_invalid_to_play_allows_non_jick_if_jick_suit_is_lead():
    game = GameFactory(num_players=3, num_teams=0)
    p1 = PlayerFactory(user=game.owner, game=game, seat=1)
    card_reps = ["JD", "2S", "3S", "4S", "5S", "6S"]
    p2 = PlayerFactory(game=game, seat=2, cards_in_hand=card_reps)
    PlayerFactory(game=game, seat=3)
    game.set_plays_after()

    trick = TrickFactory(hand__game=game, hand__trump="hearts")

    Play.objects.create(trick=trick, card="2D", player=p1)

    assert trick.is_card_invalid_to_play(Card(representation="2S"), p2) is None


@pytest.mark.django_db
def test_is_card_invalid_to_play_allows_non_jick_suit_if_jick_is_lead():
    game = GameFactory(num_players=3, num_teams=0)
    p1 = PlayerFactory(user=game.owner, game=game, seat=1)
    card_reps = ["2H", "2S", "3S", "4S", "5S", "6S"]
    p2 = PlayerFactory(game=game, seat=2, cards_in_hand=card_reps)
    PlayerFactory(game=game, seat=3)
    game.set_plays_after()

    trick = TrickFactory(hand__game=game, hand__trump="diamonds")

    # First player leads Jick
    Play.objects.create(trick=trick, card="JH", player=p1)

    # Second player should be able to play non-trump, rather than hearts
    assert trick.is_card_invalid_to_play(Card(representation="2S"), p2) is None
