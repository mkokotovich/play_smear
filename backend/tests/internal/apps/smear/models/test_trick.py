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

    Play.objects.create(trick=trick, card="AH", player=p1)
    Play.objects.create(trick=trick, card="2S", player=p2)

    trick.hand.update_if_out_of_cards(p2, Card(representation="2S"))

    assert trick.hand.players_out_of_suits["hearts"] == [str(p2.id)]
