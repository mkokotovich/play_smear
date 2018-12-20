# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS
from bidding_logic import *
from playing_logic import *
from player_input import *
from card_counting import CardCounting



class Player(object):
    def __init__(self, name, initial_cards=None, debug=False, playing_logic=None, bidding_logic=None):
        self.hand = pydealer.Stack()
        self.pile = pydealer.Stack()
        self.bid = 0
        self.bid_trump = None
        self.is_bidder = False
        self.debug = debug
        self.trick_results = None
        if initial_cards:
            self.hand += initial_cards
        self.name = name
        if playing_logic is None:
            playing_logic = JustGreedyEnough()
        self.playing_logic = playing_logic
        if bidding_logic is None:
            bidding_logic = BasicBidding(debug=debug)
        self.bidding_logic = bidding_logic
        self.player_id = None
        self.team_id = None

    def reset(self):
        self.hand = pydealer.Stack()
        self.pile = pydealer.Stack()
        self.bid = 0
        self.bid_trump = None
        self.is_bidder = False

    def set_player_id(self, player_id):
        self.player_id = player_id
        self.playing_logic.player_id = player_id

    def set_team_id(self, team_id):
        self.team_id = team_id

    def set_initial_cards(self, initial_cards):
        self.hand = pydealer.Stack()
        self.hand += initial_cards

    def receive_dealt_card(self, dealt_card):
        self.hand += dealt_card

    def print_cards(self, print_pile=False):
        msg = "{} hand: {}".format(self.name, " ".join(x.abbrev for x in self.hand))
        if print_pile:
            msg += "\n"
            msg += "{} pile: {}".format(self.name, " ".join(x.abbrev for x in self.pile))
        return msg

    # Returns a single card
    def play_card(self, current_hand, card_counting_info, teams):
        if self.hand.size == 0:
            return None
        card_index = self.playing_logic.choose_card(current_hand, card_counting_info, self.hand, teams, self.is_bidder)
        card_to_play = self.hand[card_index]
        del self.hand[card_index]
        return card_to_play

    def has_cards(self):
        return self.hand.size != 0

    def declare_bid(self, current_hand, force_two=False):
        if self.debug:
            print "{} is calculating bid".format(self.name)
        self.bidding_logic.calculate_bid(current_hand, self.hand, force_two)
        self.bid = self.bidding_logic.declare_bid()
        return self.bid

    def get_trump(self):
        self.is_bidder = True
        self.bid_trump = self.bidding_logic.declare_trump()
        return self.bid_trump

    def calculate_game_score(self):
        return utils.calculate_game_score(self.pile)

    def get_high_trump_card(self, trump):
        high_trump = None
        my_trump = utils.get_trump_indices(trump, self.pile)
        if len(my_trump) != 0:
            high_trump = self.pile[my_trump[-1]]
        return high_trump

    def has_jack_of_trump(self, trump):
        my_trump = utils.get_trump_indices(trump, self.pile)
        has_jack = False
        for idx in my_trump:
            if self.pile[idx].value == "Jack" and self.pile[idx].suit == trump:
                has_jack = True
                break
        return has_jack

    def has_jick_of_trump(self, trump):
        my_trump = utils.get_trump_indices(trump, self.pile)
        has_jick = False
        for idx in my_trump:
            if self.pile[idx].value == "Jack" and self.pile[idx].suit != trump:
                has_jick = True
                break
        return has_jick

    def add_cards_to_pile(self, cards):
        self.pile += cards

    def save_results_of_trick(self, winner_id, cards_played):
        self.trick_results = { "winner": winner_id, "cards_played": cards_played }

    def get_results_of_trick(self):
        results = self.trick_results
        self.trick_results = None
        return results

    def __str__(self):
        return "{}: {}".format(self.name, " ".join(x.abbrev for x in self.hand))


class InteractivePlayer(Player):
    def __init__(self, player_id, initial_cards=None, debug=False):
        super(InteractivePlayer, self).__init__(player_id, initial_cards, debug)
        self.playing_logic = PlayerInput(debug=debug)
        self.bidding_logic = self.playing_logic

    def reset(self):
        super(InteractivePlayer, self).reset()
        self.playing_logic.reset()

    def get_hand(self):
        my_hand = [ { "suit": card.suit, "value": card.value} for card in self.hand ]
        if len(my_hand) == 0:
            my_hand = None
        return my_hand

    def get_bid_info(self):
        return self.bidding_logic.get_bid_info()

    def save_bid(self, bid):
        self.bidding_logic.save_bid(bid)

    def save_trump(self, trump):
        return self.bidding_logic.save_trump(trump)

    def get_playing_info(self):
        return self.playing_logic.get_playing_info()

    def save_card_to_play(self, card_to_play, trump):
        return self.playing_logic.save_card_to_play(card_to_play, trump)
