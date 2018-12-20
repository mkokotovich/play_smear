import unittest
import sys

sys.path.insert(0, "..")
import pysmear.bidding_logic
import pydealer

class TestBiddingLogic(unittest.TestCase):
    def setUp(self):
        self.bl = pysmear.bidding_logic.BasicBidding()
        self.num_players = 3
        self.suit = "Spades"
        self.ace_spades = pydealer.Card("Ace", "Spades")
        self.two_diamonds = pydealer.Card("2", "Diamonds")
        self.queen_hearts = pydealer.Card("Queen", "Hearts")
        self.seven_clubs = pydealer.Card("7", "Clubs")
        self.jack_clubs = pydealer.Card("Jack", "Clubs")
        self.two_spades = pydealer.Card("2", "Spades")
        self.cards = [self.ace_spades, self.two_diamonds, self.queen_hearts,
            self.seven_clubs, self.jack_clubs, self.two_spades]
        self.my_hand = pydealer.Stack(cards=self.cards)

    def test_expected_points_from_jack_and_jick(self):
        jj = self.bl.expected_points_from_jack_and_jick(self.num_players, self.my_hand, self.suit)
        self.assertEqual(jj, 0.75)
