import unittest
from mock import MagicMock
import sys

sys.path.insert(0, "..")
from pysmear.smear_utils import SmearUtils as utils
from pysmear.card_counting import CardCounting
import pydealer


class TestSafeToPlay(unittest.TestCase):
    def setUp(self):
        self.cc = CardCounting(num_players = 4)
        self.trump = "Spades"
        self.current_trick = MagicMock()
        self.current_trick.trump = self.trump
        self.current_trick.lead_suit = "Trump"

        self.jack_hearts = pydealer.Card(value="Jack", suit="Hearts")
        self.jack_spades = pydealer.Card(value="Jack", suit="Spades")
        self.jack_diamonds = pydealer.Card(value="Jack", suit="Diamonds")
        self.jack_clubs = pydealer.Card(value="Jack", suit="Clubs")

        self.ace_spades = pydealer.Card("Ace", "Spades")
        self.king_spades = pydealer.Card("King", "Spades")
        self.queen_spades = pydealer.Card("Queen", "Spades")
        self.ten_spades = pydealer.Card("10", "Spades")

        self.two_diamonds = pydealer.Card("2", "Diamonds")
        self.queen_hearts = pydealer.Card("Queen", "Hearts")
        self.seven_clubs = pydealer.Card("7", "Clubs")
        self.two_spades = pydealer.Card("2", "Spades")
        self.cards = [self.ace_spades, self.two_diamonds, self.queen_hearts,
            self.seven_clubs, self.jack_clubs, self.two_spades]

        self.current_trick.cards = self.cards


    def test_jick_is_safe_after_a_k_q_j(self):
        self.cc.cards_played["Trump"].append(self.ace_spades)
        self.cc.cards_played["Trump"].append(self.king_spades)
        self.cc.cards_played["Trump"].append(self.queen_spades)
        self.cc.cards_played["Trump"].append(self.jack_spades)

        self.current_trick.cards = [ self.two_diamonds ]
        safe = self.cc.safe_to_play(0, self.jack_clubs, self.current_trick, [])
        self.assertEqual(safe, True)


    def test_two_is_safe_after_everyone_is_out_of_trump(self):
        self.cc.card_was_played(0, self.ace_spades, self.current_trick)
        self.cc.card_was_played(1, self.two_diamonds, self.current_trick)
        self.cc.card_was_played(2, self.queen_hearts, self.current_trick)
        self.cc.card_was_played(3, self.seven_clubs, self.current_trick)

        self.current_trick.cards = []
        safe = self.cc.safe_to_play(0, self.two_spades, self.current_trick, [])
        self.assertEqual(safe, True)

    def test_jick_is_safe_if_only_player_behind_me_is_out(self):
        self.cc.player_out_of_cards[1]["Trump"] = True
        self.current_trick.cards = [ self.two_diamonds, self.seven_clubs ]
        safe = self.cc.safe_to_play(0, self.jack_clubs, self.current_trick, [])
        self.assertEqual(safe, True)


class TestHighestCardStillOut(unittest.TestCase):
    def setUp(self):
        self.cc = CardCounting(num_players = 4)
        self.trump = "Spades"
        self.current_trick = MagicMock()
        self.current_trick.trump = self.trump
        self.current_trick.lead_suit = self.trump

        self.jack_hearts = pydealer.Card(value="Jack", suit="Hearts")
        self.jack_spades = pydealer.Card(value="Jack", suit="Spades")
        self.jack_diamonds = pydealer.Card(value="Jack", suit="Diamonds")
        self.jack_clubs = pydealer.Card(value="Jack", suit="Clubs")

        self.ace_spades = pydealer.Card("Ace", "Spades")
        self.king_spades = pydealer.Card("King", "Spades")
        self.queen_spades = pydealer.Card("Queen", "Spades")
        self.ten_spades = pydealer.Card("10", "Spades")

        self.two_diamonds = pydealer.Card("2", "Diamonds")
        self.queen_hearts = pydealer.Card("Queen", "Hearts")
        self.seven_clubs = pydealer.Card("7", "Clubs")
        self.two_spades = pydealer.Card("2", "Spades")
        self.cards = [self.ace_spades, self.two_diamonds, self.queen_hearts,
            self.seven_clubs, self.jack_clubs, self.two_spades]

        self.current_trick.cards = self.cards


    def test_jick_is_highest_after_a_k_q_j(self):
        self.cc.cards_played["Trump"].append(self.ace_spades)
        self.cc.cards_played["Trump"].append(self.king_spades)
        self.cc.cards_played["Trump"].append(self.queen_spades)
        self.cc.cards_played["Trump"].append(self.jack_spades)

        card = self.cc.highest_card_still_out("Spades", True)
        self.assertEqual(card, self.jack_clubs)

    def test_10_is_highest_after_a_k_q_j_j(self):
        self.cc.cards_played["Trump"].append(self.ace_spades)
        self.cc.cards_played["Trump"].append(self.king_spades)
        self.cc.cards_played["Trump"].append(self.queen_spades)
        self.cc.cards_played["Trump"].append(self.jack_spades)
        self.cc.cards_played["Trump"].append(self.jack_clubs)

        card = self.cc.highest_card_still_out("Spades", True)
        self.assertEqual(card, self.ten_spades)

    def test_ace_is_highest(self):
        card = self.cc.highest_card_still_out("Spades", True)
        self.assertEqual(card, self.ace_spades)

    def test_ace_is_still_highest_after_played_if_ignored(self):
        card = self.cc.highest_card_still_out("Spades", True, self.ace_spades)
        self.assertEqual(card, self.ace_spades)

