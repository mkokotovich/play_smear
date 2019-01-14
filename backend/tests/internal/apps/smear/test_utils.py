from apps.smear.utils import Card

import pytest


@pytest.mark.parametrize('rep,exp_value,exp_suit',
    [
        ('2S', '2', 'spades'),
        ('AH', 'ace', 'hearts'),
        ('KC', 'king', 'clubs'),
        ('QD', 'queen', 'diamonds'),
        ('JS', 'jack', 'spades'),
        ('0S', '10', 'spades'),
    ]
)
def test_Card_representation_to_value_and_suit(rep, exp_value, exp_suit):
    card = Card(rep)

    assert card.value == exp_value
    assert card.suit == exp_suit


@pytest.mark.parametrize('exp_rep,value,suit',
    [
        ('2S', '2', 'spades'),
        ('AH', 'ace', 'hearts'),
        ('KC', 'king', 'clubs'),
        ('QD', 'queen', 'diamonds'),
        ('JS', 'jack', 'spades'),
        ('0S', '10', 'spades'),
    ]
)
def test_Card_to_representation(exp_rep, value, suit):
    card = Card("2S")
    card.value = value
    card.suit = suit
    rep = card.to_representation()

    assert rep == exp_rep

