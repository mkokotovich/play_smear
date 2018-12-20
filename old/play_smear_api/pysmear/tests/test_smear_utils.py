import unittest
import sys

sys.path.insert(0, "..")
from pysmear.smear_utils import SmearUtils as utils
import pydealer
from pydealer.const import POKER_RANKS


class TestIsTrump(unittest.TestCase):
    def setUp(self):
        self.trump = "Spades"
        self.jack_hearts = pydealer.Card(value="Jack", suit="Hearts")
        self.jack_spades = pydealer.Card(value="Jack", suit="Spades")
        self.jack_diamonds = pydealer.Card(value="Jack", suit="Diamonds")
        self.jack_clubs = pydealer.Card(value="Jack", suit="Clubs")

        self.ace_spades = pydealer.Card("Ace", "Spades")
        self.two_diamonds = pydealer.Card("2", "Diamonds")
        self.queen_hearts = pydealer.Card("Queen", "Hearts")
        self.seven_clubs = pydealer.Card("7", "Clubs")
        self.two_spades = pydealer.Card("2", "Spades")
        self.cards = [self.ace_spades, self.two_diamonds, self.queen_hearts,
            self.seven_clubs, self.jack_clubs, self.two_spades]
        self.my_hand = pydealer.Stack(cards=self.cards)

    def test_non_jick_non_trump(self):
        is_trump = utils.is_trump(self.two_diamonds, self.trump)
        self.assertEqual(is_trump, False)

    def test_non_jick_non_trump_jack(self):
        is_trump = utils.is_trump(self.jack_hearts, self.trump)
        self.assertEqual(is_trump, False)

    def test_non_jick_trump(self):
        is_trump = utils.is_trump(self.two_spades, self.trump)
        self.assertEqual(is_trump, True)

    def test_jack_trump_spades(self):
        self.trump = "Spades"
        is_trump = utils.is_trump(self.jack_spades, self.trump)
        self.assertEqual(is_trump, True)

    def test_jick_trump_spades(self):
        self.trump = "Spades"
        is_trump = utils.is_trump(self.jack_clubs, self.trump)
        self.assertEqual(is_trump, True)

    def test_jack_trump_hearts(self):
        self.trump = "Hearts"
        is_trump = utils.is_trump(self.jack_hearts, self.trump)
        self.assertEqual(is_trump, True)

    def test_jick_trump_hearts(self):
        self.trump = "Hearts"
        is_trump = utils.is_trump(self.jack_diamonds, self.trump)
        self.assertEqual(is_trump, True)

    def test_jack_trump_diamonds(self):
        self.trump = "Diamonds"
        is_trump = utils.is_trump(self.jack_diamonds, self.trump)
        self.assertEqual(is_trump, True)

    def test_jick_trump_diamonds(self):
        self.trump = "Diamonds"
        is_trump = utils.is_trump(self.jack_hearts, self.trump)
        self.assertEqual(is_trump, True)

    def test_jack_trump_clubs(self):
        self.trump = "Clubs"
        is_trump = utils.is_trump(self.jack_clubs, self.trump)
        self.assertEqual(is_trump, True)

    def test_jick_trump_clubs(self):
        self.trump = "Clubs"
        is_trump = utils.is_trump(self.jack_spades, self.trump)
        self.assertEqual(is_trump, True)



class TestInsertCard(unittest.TestCase):
    def setUp(self):
        self.trump = "Spades"
        self.jack_spades = pydealer.Card(value="Jack", suit="Spades")
        self.jack_clubs = pydealer.Card(value="Jack", suit="Clubs")
        self.ace_spades = pydealer.Card(value="Ace", suit="Spades")
        self.two_spades = pydealer.Card(value="2", suit="Spades")
        self.nine_spades = pydealer.Card(value="9", suit="Spades")

        self.queen_spades = pydealer.Card("Queen", "Spades")
        self.ten_spades = pydealer.Card("10", "Spades")
        self.seven_spades = pydealer.Card("7", "Spades")
        self.four_spades = pydealer.Card("4", "Spades")
        self.cards = [self.queen_spades, self.ten_spades, self.seven_spades, self.four_spades]
        self.my_hand = pydealer.Stack(cards=self.cards)
        self.trump_indices = self.my_hand.find(self.trump, sort=True, ranks=POKER_RANKS)

    def test_inserting_middle(self):
        self.my_hand.add([self.nine_spades])
        before_len = len(self.trump_indices)
        utils.insert_card_into_sorted_index_list(self.trump_indices, self.my_hand, self.my_hand.find(self.nine_spades.abbrev)[0])
        after_len = len(self.trump_indices)
        self.assertEqual(before_len+1, after_len)
        self.assertEqual(self.trump_indices[2], 4)

    def test_inserting_beginning(self):
        self.my_hand.add([self.two_spades])
        before_len = len(self.trump_indices)
        utils.insert_card_into_sorted_index_list(self.trump_indices, self.my_hand, self.my_hand.find(self.two_spades.abbrev)[0])
        after_len = len(self.trump_indices)
        self.assertEqual(before_len+1, after_len)
        self.assertEqual(self.trump_indices[0], 4)

    def test_inserting_end(self):
        self.my_hand.add([self.ace_spades])
        before_len = len(self.trump_indices)
        utils.insert_card_into_sorted_index_list(self.trump_indices, self.my_hand, self.my_hand.find(self.ace_spades.abbrev)[0])
        after_len = len(self.trump_indices)
        self.assertEqual(before_len+1, after_len)
        self.assertEqual(self.trump_indices[4], 4)


class TestGetTrumpIndices(unittest.TestCase):
    def setUp(self):
        self.trump = "Spades"
        self.jack_spades = pydealer.Card(value="Jack", suit="Spades")
        self.jack_clubs = pydealer.Card(value="Jack", suit="Clubs")
        self.ace_spades = pydealer.Card(value="Ace", suit="Spades")
        self.two_clubs = pydealer.Card(value="2", suit="Clubs")
        self.two_hearts = pydealer.Card(value="2", suit="Hearts")
        self.nine_spades = pydealer.Card(value="9", suit="Spades")
        self.six_hearts = pydealer.Card("6", "Hearts")
        self.seven_hearts = pydealer.Card("7", "Hearts")
        self.nine_clubs = pydealer.Card(value="9", suit="Clubs")
        self.queen_diamonds = pydealer.Card(value="Queen", suit="Diamonds")

        self.queen_spades = pydealer.Card("Queen", "Spades")
        self.ten_spades = pydealer.Card("10", "Spades")
        self.seven_spades = pydealer.Card("7", "Spades")
        self.four_spades = pydealer.Card("4", "Spades")
        self.cards = [self.queen_spades, self.ten_spades, self.seven_spades, self.four_spades]
        self.my_hand = pydealer.Stack(cards=self.cards)

    def test_with_two_trump_with_jick_high_and_one_other_card(self):
        self.cards = [self.jack_clubs, self.nine_spades, self.two_hearts]
        self.my_hand = pydealer.Stack(cards=self.cards)
        indices = utils.get_trump_indices(self.trump, self.my_hand)
        self.assertEqual(2, len(indices))
        self.assertEqual(indices[0], self.cards.index(self.nine_spades))
        self.assertEqual(indices[1], self.cards.index(self.jack_clubs))

    def test_with_one_trump_with_jick_high_and_one_other_card(self):
        self.cards = [self.jack_clubs, self.two_hearts]
        self.my_hand = pydealer.Stack(cards=self.cards)
        indices = utils.get_trump_indices(self.trump, self.my_hand)
        self.assertEqual(1, len(indices))
        self.assertEqual(indices[0], self.cards.index(self.jack_clubs))

    def test_with_one_trump_with_jick_high_and_four_other_cards(self):
        self.cards = [self.six_hearts, self.seven_hearts, self.nine_clubs, self.jack_clubs, self.queen_diamonds]
        self.my_hand = pydealer.Stack(cards=self.cards)
        indices = utils.get_trump_indices(self.trump, self.my_hand)
        self.assertEqual(1, len(indices))
        self.assertEqual(indices[0], self.cards.index(self.jack_clubs))


class TestGetLegalPlayIndices(unittest.TestCase):
    def setUp(self):
        self.trump = "Spades"
        self.jack_spades = pydealer.Card(value="Jack", suit="Spades")
        self.jack_clubs = pydealer.Card(value="Jack", suit="Clubs")
        self.ace_spades = pydealer.Card(value="Ace", suit="Spades")
        self.two_clubs = pydealer.Card(value="2", suit="Clubs")
        self.two_hearts = pydealer.Card(value="2", suit="Hearts")
        self.nine_spades = pydealer.Card(value="9", suit="Spades")
        self.six_hearts = pydealer.Card("6", "Hearts")
        self.seven_hearts = pydealer.Card("7", "Hearts")
        self.nine_clubs = pydealer.Card(value="9", suit="Clubs")
        self.queen_diamonds = pydealer.Card(value="Queen", suit="Diamonds")

        self.queen_spades = pydealer.Card("Queen", "Spades")
        self.ten_spades = pydealer.Card("10", "Spades")
        self.seven_spades = pydealer.Card("7", "Spades")
        self.four_spades = pydealer.Card("4", "Spades")

    def test_jick_is_only_club_when_clubs_lead(self):
        self.cards = [self.six_hearts, self.seven_hearts, self.ten_spades, self.jack_clubs, self.queen_diamonds]
        self.my_hand = pydealer.Stack(cards=self.cards)
        indices = utils.get_legal_play_indices("Clubs", self.trump, self.my_hand)
        self.assertEqual(len(self.cards), len(indices))

