# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS
from smear_utils import SmearUtils as utils
#from stats import SmearStats


class Trick:
    def __init__(self, trump, debug=False):
        # This list is in order of cards played
        self.cards = []
        # This is a list of cards played with the player who played them
        self.cards_played = []
        self.trump = trump 
        # This will either be "Trump" or "Spades", "Diamonds", "Hearts", or "Clubs"
        self.lead_suit = ""
        self.current_winner_id = 0
        self.current_winning_card = None
        self.debug = debug

    def is_new_card_higher(self, card):
        return utils.is_new_card_higher(self.current_winning_card, card, self.trump, debug=self.debug)

    def add_card(self, player_id, card):
        if len(self.cards) == 0:
            # This is the first card
            if utils.is_trump(card, self.trump):
                self.lead_suit = "Trump"
            else:
                self.lead_suit = card.suit
            self.current_winning_card = card
            self.current_winner_id = player_id
        elif self.is_new_card_higher(card):
            self.current_winning_card = card
            self.current_winner_id = player_id
        self.cards.append(card)
        self.cards_played.append({ "username": player_id, "card": { "suit": card.suit, "value": card.value }})

    def get_winner_id(self):
        return self.current_winner_id

    def get_all_cards_as_stack(self):
        stack = pydealer.Stack()
        for x in self.cards:
            stack += [x]
        return stack

    def get_cards_played(self):
        return self.cards_played
