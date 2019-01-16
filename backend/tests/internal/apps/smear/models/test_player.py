import pytest

from django.contrib.auth.models import User

from apps.smear.models import Player
from apps.smear.cards import Deck
from tests.internal.apps.smear.factories import PlayerFactory


@pytest.mark.parametrize(
    'expected_name,user',
    [
        ('Unknown', None),
        ('Bob M', User(username="bob_mcbob@gmail.com", first_name="Bob", last_name="McBob")),
        ('bob_mcbob', User(username="bob_mcbob@gmail.com", first_name="", last_name="")),
    ]
)
def test_get_name_from_user(expected_name, user):
    player = Player()

    name = player._get_name_from_user(user)

    assert name == expected_name


@pytest.mark.django_db
def test_accept_dealt_cards():
    player = PlayerFactory()
    deck = Deck()

    cards = deck.deal(3)
    player.accept_dealt_cards(cards)

    player.refresh_from_db()
    assert player.cards_in_hand == [card.to_representation() for card in cards]
    assert player.get_cards() == cards
