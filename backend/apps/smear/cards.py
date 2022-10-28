import logging
import copy
import random


LOG = logging.getLogger(__name__)

SPADES = 'spades'
HEARTS = 'hearts'
CLUBS = 'clubs'
DIAMONDS = 'diamonds'
SUITS = [SPADES, HEARTS, CLUBS, DIAMONDS]
SUIT_CHOICES = ((suit, suit) for suit in SUITS)


class Card():
    def _representation_to_value_and_suit(self, representation):
        value = {
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '0': '10',
            'J': 'jack',
            'Q': 'queen',
            'K': 'king',
            'A': 'ace',
        }.get(representation[0:1], None)

        suit = {
            'S': SPADES,
            'H': HEARTS,
            'C': CLUBS,
            'D': DIAMONDS,
        }.get(representation[1:2], None)

        if not value or not suit:
            raise ValueError(f"Unable to parse card representation: {representation}")

        return value, suit

    def rank(self):
        rank = {
            '2': 1,
            '3': 2,
            '4': 3,
            '5': 4,
            '6': 5,
            '7': 6,
            '8': 7,
            '9': 8,
            '10': 9,
            'jack': 10,
            'queen': 11,
            'king': 12,
            'ace': 13,
        }.get(self.value, None)

        if not rank:
            raise ValueError(f"Unable to find rank for value: {self.value}")

        return rank

    def trump_rank(self, trump):
        rank = {
            '2': 1,
            '3': 2,
            '4': 3,
            '5': 4,
            '6': 5,
            '7': 6,
            '8': 7,
            '9': 8,
            '10': 9,
            'jack': None,
            'queen': 12,
            'king': 13,
            'ace': 14,
        }.get(self.value)

        # Differentiate between jack and jick
        if not rank:
            rank = 11 if self.suit == trump else 10

        return rank

    def __init__(self, representation=None, value=None, suit=None):
        value, suit = self._representation_to_value_and_suit(representation) if representation else (value, suit)
        if not value or not suit:
            raise ValueError("value and suit must be provided, either by representation or through parameters")
        self.value = value
        self.suit = suit

    def __str__(self):
        return f"{self.to_representation()}"

    def __repr__(self):
        return self.__str__()

    @property
    def pretty(self):
        return f"{self.value} of {self.suit}"

    def __eq__(self, other):
        return other and self.value == other.value and self.suit == other.suit

    @property
    def representation(self):
        return self.to_representation()

    def to_representation(self):
        value = {
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '0',
            'jack': 'J',
            'queen': 'Q',
            'king': 'K',
            'ace': 'A',
        }.get(self.value, None)

        suit = {
            SPADES: 'S',
            HEARTS: 'H',
            CLUBS: 'C',
            DIAMONDS: 'D',
        }.get(self.suit, None)

        if not value or not suit:
            raise ValueError(f"Unable to convert card to representation: value: {self.value} suit: {self.suit}")

        return value + suit

    def _same_color(self, suit):
        if self.suit == HEARTS or self.suit == DIAMONDS:
            return suit == HEARTS or suit == DIAMONDS
        if self.suit == CLUBS or self.suit == SPADES:
            return suit == CLUBS or suit == SPADES

    def is_trump(self, trump):
        if self.suit == trump:
            return True

        if self.value == 'jack':
            return self._same_color(trump)

        return False

    def is_jick(self, trump):
        return self.value == 'jack' and self.suit != trump and self._same_color(trump)

    def is_jack(self, trump):
        return self.value == 'jack' and self.suit == trump

    def is_less_than(self, other, trump):
        less_than = False
        if other is None:
            less_than = False
        elif self.is_trump(trump) and not other.is_trump(trump):
            # self is trump and other isn't, return false
            less_than = False
        elif not self.is_trump(trump) and other.is_trump(trump):
            # self is not trump and other is, return true
            less_than = True
        elif self.is_trump(trump):
            # Both are trump
            if self.suit == other.suit:
                # Neither are Jicks, just compare
                less_than = self.rank() < other.rank()
            else:
                # One of the cards is the jick
                if self.suit != trump:
                    # self is a jick, if both are value=jack than self is less
                    less_than = self.rank() <= other.rank()
                else:
                    # other is a jick, if both are value=jack than self is not less
                    less_than = self.rank() < other.rank()
        else:
            # Neither are trump
            if other.suit != self.suit:
                # When deciding who takes a trick between two non-trump cards,
                # if the other card didn't follow suit it isn't greater than
                # our card
                less_than = False
            else:
                # Both cards are same suit, just compare rank
                less_than = self.rank() < other.rank()

        return less_than

    @property
    def game_points(self):
        return {
            '10': 10,
            'jack': 1,
            'queen': 2,
            'king': 3,
            'ace': 4,
        }.get(self.value, 0)


class Deck():
    ALL_CARDS = [
        Card(value=value, suit=suit)
        for value in
        [
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9',
            '10',
            'jack',
            'queen',
            'king',
            'ace',
        ]
        for suit in SUITS
    ]

    def __init__(self):
        self.reset()

    def reset(self):
        self.cards = copy.deepcopy(self.ALL_CARDS)
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num=3):
        # Deals num cards, returning a list of cards
        return [self.cards.pop(0) for x in range(0, num)]
