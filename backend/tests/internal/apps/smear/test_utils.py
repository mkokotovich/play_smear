import copy

import pytest

from apps.smear.cards import Card, Deck


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


def test_Deck_shuffle_mixes_up_the_cards():
    deck = Deck()
    old_cards = copy.deepcopy(deck.cards)

    deck.shuffle()

    assert old_cards != deck.cards


def test_Deck_has_52_cards():
    deck = Deck()
    assert len(deck.cards) == 52
    for suit in ['spades', 'diamonds', 'clubs', 'hearts']:
        suit_cards = [card for card in deck.cards if card.suit == suit]
        assert len(suit_cards) == 13


def test_Deck_deal():
    deck = Deck()
    old_cards = copy.deepcopy(deck.cards)

    cards = deck.deal()

    assert len(deck.cards) == 49
    assert len(cards) == 3
    assert cards == old_cards[0:3]
