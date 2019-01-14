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
            'S': 'spades',
            'H': 'hearts',
            'C': 'clubs',
            'D': 'diamonds',
        }.get(representation[1:2], None)

        if not value or not suit:
            raise ValueError(f"Unable to parse card representation: {representation}")

        return value, suit

    def rank(self):
        rank =  {
            '2': 1,
            '3': 2,
            '4': 3,
            '5': 4,
            '6': 5,
            '7': 6,
            '8': 7,
            '9': 8,
            '0': 9,
            'J': 10,
            'Q': 11,
            'K': 12,
            'A': 13,
        }.get(self.value, None)

        if not rank:
            raise ValueError(f"Unable to find rank for value: {self.value}")

        return rank

    def __init__(self, representation=None, def_value=None, def_suit=None):
        value, suit = self._representation_to_value_and_suit(representation) if representation else (def_value, def_suit)
        self.value = value
        self.suit = suit

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
            'spades': 'S',
            'hearts': 'H',
            'clubs': 'C',
            'diamonds': 'D',
        }.get(self.suit, None)

        if not value or not suit:
            raise ValueError(f"Unable to convert card to representation: value: {self.value} suit: {self.suit}")

        return value + suit

    def _same_color(self, suit):
        if self.suit == 'hearts' or self.suit == 'diamonds':
            return suit == 'hearts' or suit == 'diamonds'
        if self.suit == 'clubs' or self.suit == 'spades':
            return suit == 'clubs' or suite == 'spades'

    def is_trump(self, trump):
        if self.suit == trump:
            return True

        if self.value == 'j':
            return self._same_color(trump)

    def is_less_than(self, other, trump):
        less_than = False
        if other == None:
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
            # Neither are trump, just compare values (although this isn't how tricks are taken)
            log.warning("Warning, comparing cards with different suits")
            less_than = self.rank() < other.rank()

        return less_than
