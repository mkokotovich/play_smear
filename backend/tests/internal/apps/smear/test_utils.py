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


@pytest.mark.parametrize(
    'exp_rep,value,suit',
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
    card = Card(value=value, suit=suit)
    rep = card.to_representation()

    assert rep == exp_rep

@pytest.mark.parametrize(
    'value,suit,expected_is_trump',
    [
        ('ace', 'spades', True),
        ('jack', 'spades', True),
        ('jack', 'clubs', True),
        ('jack', 'diamonds', False),
        ('jack', 'hearts', False),
        ('2', 'hearts', False),
        ('2', 'spades', True),
    ]
)
def test_Card_is_trump(value, suit, expected_is_trump):
    card = Card(value=value, suit=suit)
    assert expected_is_trump == card.is_trump('spades')

@pytest.mark.parametrize(
    'value,suit,other,trump,expected_less_than',
    [
        ('ace', 'spades', Card(representation='KS'), 'spades', False),
        ('2', 'spades', Card(representation='AS'), 'spades', True),
        ('jack', 'spades', Card(representation='JC'), 'spades', False),
        ('jack', 'clubs', Card(representation='JS'), 'spades', True),
        ('jack', 'clubs', Card(representation='JH'), 'spades', False),
        ('jack', 'diamonds', Card(representation='2S'), 'spades', True),
    ]
)
def test_Card_is_less_than(value, suit, other, trump, expected_less_than):
    assert Card(value=value, suit=suit).is_less_than(other, trump) == expected_less_than
