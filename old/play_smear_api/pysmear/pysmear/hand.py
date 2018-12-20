# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS
from smear_utils import SmearUtils as utils
from trick import Trick
from card_counting import CardCounting
from playing_logic import CautiousTaker
from bidding_logic import BetterBidding


# Everything regarding the state of a hand, so a player can look at this and chose a card to play
class SmearHand:
    def __init__(self, num_players, debug=False):
        self.num_players = num_players
        self.trump = ""
        self.bid = 0
        self.bidder = 0
        self.first_player = 0
        self.debug = debug
        self.current_trick = Trick(self.trump, debug)
        self.all_bids = []

    def set_trump(self, trump):
        self.trump = trump
        self.current_trick.trump = trump

    def add_card(self, player_id, card):
        if card is not None:
            self.current_trick.add_card(player_id, card)

    def prepare_for_next_trick(self):
        self.current_trick = Trick(self.trump, self.debug)

    def get_cards_played(self):
        return self.current_trick.get_cards_played()

    def add_bid(self, player_id, bid):
        self.all_bids.append({ "game_id": "", "username": player_id, "bid": bid })

    def get_all_bids(self):
        return self.all_bids


# A hand is one deal, play until all cards are out, and tally the score iteration
class SmearHandManager:
    def __init__(self, players_dict, num_teams, cards_to_deal=6, debug=False):
        self.players = players_dict
        self.num_players = len(players_dict.values())
        self.num_teams = num_teams
        self.cards_to_deal = cards_to_deal
        self.deck = pydealer.Deck(ranks=POKER_RANKS)
        if self.num_players * cards_to_deal > self.deck.size:
            raise ValueError("num_players ({}) times cards_to_deal ({}) is larger than the size of the deck ({})".format(self.num_players, cards_to_deal, deck.size))
        self.reset_players()
        self.current_hand_id = 0
        self.current_hand = SmearHand(self.num_players, debug)
        self.scores = {}
        self.current_low_id = 0
        self.current_low = None
        self.all_bids_are_in = False
        self.remaining_bids = self.num_players
        self.current_bidder = 0
        self.forced_two_set = False
        self.hand_results = {}
        self.debug = debug
        self.remaining_players = self.num_players
        self.current_player = 0
        self.card_counting_info = CardCounting(self.num_players, self.debug)
        self.teams = []
        self.add_players_to_teams()

    def reset_players(self):
        for i in range(0, self.num_players):
            self.players[i].reset()

    def add_players_to_teams(self):
        # Add empty array for each team
        for _ in range(0, self.num_teams):
            self.teams.append([])
        for i in range(0, self.num_players):
            if self.players[i].team_id is not None:
                # Add player_id to team
                self.teams[self.players[i].team_id].append(self.players[i].player_id)

    def deal_new_deck(self):
        self.deck = pydealer.Deck(ranks=POKER_RANKS)
        self.deck.shuffle()
        for j in range(0, self.cards_to_deal):
            for i in range(0, self.num_players):
                self.players[i].receive_dealt_card(self.deck.deal(1))

    def reset_for_next_hand(self):
        self.reset_players()
        self.deal_new_deck()
        self.current_hand_id += 1
        self.current_hand = SmearHand(self.num_players, self.debug)
        self.scores = {}
        self.hand_results = {}
        self.current_low_id = 0
        self.current_low = None
        self.all_bids_are_in = False
        self.remaining_bids = self.num_players
        self.current_bidder = 0
        self.forced_two_set = False
        self.card_counting_info.reset_for_next_hand()

    def prepare_for_next_trick(self):
        self.current_hand.prepare_for_next_trick()
        self.remaining_players = self.num_players
        self.current_player = 0

    def is_hand_over(self):
        for player in self.players.values():
            if player.has_cards():
                return False
        return True


    def set_players_score_to(self, player_id, points):
        self.scores[player_id] = points


    def add_point_to_a_players_score(self, player_id):
        self.scores[player_id] += 1


    def player_was_set(self, player_id, points):
        self.add_to_score(player_id, was_set=True, set_points=points)


    def add_to_score(self, player_id, was_set=False, set_points=0):
        if len(self.teams) > 0:
            # We are playing with teams. Add the points to each member of the team.
            team_to_add = None
            for team in self.teams:
                if player_id in team:
                    team_to_add = team
                    break
            if team_to_add is None:
                print "Unable to find player {} in any team".format(player_id)
                return
            for player in team_to_add:
                if not was_set:
                    self.add_point_to_a_players_score(player)
                else:
                    self.set_players_score_to(player, set_points)
        else:
            # Not playing with teams, just add the points to the player
            if not was_set:
                self.add_point_to_a_players_score(player_id)
            else:
                self.set_players_score_to(player_id, set_points)


    def calculate_game_winner(self):
        game_winning_score = 0
        game_winning_id = None
        current_winning_players = []
        if len(self.teams) > 0:
            # We are playing with teams. Sum the game points for each member. But keep track of
            # only one player per team, as that is what the GUI will show
            for team in self.teams:
                team_game_score = 0
                high_player_score = 0
                high_player_id = 0
                for player_id in team:
                    # Find that player's game score
                    player_score = self.players[player_id].calculate_game_score()
                    # Add the score to the team game score
                    team_game_score += player_score
                    # Determine if this is the player that should "win" game in the UI
                    if high_player_score < player_score:
                        high_player_score = player_score
                        high_player_id = player_id
                if game_winning_score < team_game_score:
                    game_winning_score = team_game_score
                    current_winning_players = [ high_player_id ]
                elif game_winning_score == team_game_score:
                    current_winning_players.append(high_player_id)
        else:
            # Not playing with teams, just find the player's score
            for player_id in range(0, self.num_players):
                game_score = self.players[player_id].calculate_game_score()
                if game_winning_score < game_score:
                    game_winning_score = game_score
                    current_winning_players = [ player_id ]
                elif game_winning_score == game_score:
                    current_winning_players.append(player_id)
        # Check to make sure there is no tie
        if len(current_winning_players) != 1:
            # Tie, no one wins
            if self.debug:
                print "No one won game, there was a tie at {} points between {}".format(game_winning_score, ", ".join(self.players[x].name for x in current_winning_players))
            return None
        else:
            # We have a winner
            game_winning_id = current_winning_players[0]

        if self.debug:
            print "{} won game with {} points".format(self.players[game_winning_id].name, game_winning_score)
        return game_winning_id


    def get_scores(self, dealer_id):
        if self.forced_two_set:
            self.scores = {}
            for i in range(0, self.num_players):
                self.scores[i] = 0
            self.player_was_set(dealer_id, -2)
            return self.scores

        if not self.is_hand_over():
            print "Hand isn't over yet"
            return None
        self.scores = {}
        current_high_id = 0
        current_high = None
        jack_id = None
        jick_id = None
        game_winning_id = self.calculate_game_winner()
        for i in range(0, self.num_players):
            # Initialize each player's score
            self.scores[i] = 0
            # Check to see if we have high
            high = self.players[i].get_high_trump_card(self.current_hand.trump)
            if (not high == None) and (current_high == None or utils.is_less_than(current_high, high, self.current_hand.trump)):
                current_high = high
                current_high_id = i
            # Check to see if we have jack
            if self.players[i].has_jack_of_trump(self.current_hand.trump):
                jack_id = i
            # Check to see if we have jick
            if self.players[i].has_jick_of_trump(self.current_hand.trump):
                jick_id = i
        # Award high
        self.add_to_score(current_high_id)
        self.hand_results["high_winner"] = current_high_id
        if self.debug:
            print "{} won high with a {}".format(self.players[current_high_id].name, current_high)
        # Award low
        self.add_to_score(self.current_low_id)
        self.hand_results["low_winner"] = self.current_low_id
        if self.debug:
            print "{} won low with a {}".format(self.players[self.current_low_id].name, self.current_low)
        # Award jack, if it was won
        if jack_id is not None:
            self.add_to_score(jack_id)
            self.hand_results["jack_winner"] = jack_id
            if self.debug:
                print "{} won jack".format(self.players[jack_id].name)
        # Award jick, if it was won
        if jick_id is not None:
            self.add_to_score(jick_id)
            self.hand_results["jick_winner"] = jick_id
            if self.debug:
                print "{} won jick".format(self.players[jick_id].name)
        # Award game. No ties for game, so if game_winning_id is None do not award game
        if game_winning_id is not None:
            self.add_to_score(game_winning_id)
            self.hand_results["game_winner"] = game_winning_id
        else:
            self.hand_results["game_winner"] = ""
        # Check to see if bidder was set
        if self.scores[self.current_hand.bidder] < self.current_hand.bid:
            if self.debug:
                print "BID: {} bid {} and only got {}: is set!".format(self.players[self.current_hand.bidder].name, self.current_hand.bid, self.scores[self.current_hand.bidder])
            self.player_was_set(self.current_hand.bidder, -self.current_hand.bid)
            self.hand_results["bidder_set"] = True
        else:
            if self.debug:
                print "BID: {} got their bid of {} with {} points".format(self.players[self.current_hand.bidder].name, self.current_hand.bid, self.scores[self.current_hand.bidder])
            self.hand_results["bidder_set"] = False

        return self.scores

    def get_players(self):
        return self.players.values()

    def post_hand_summary(self):
        msg = ""
        for i in range(0, self.num_players):
            msg +=  "{} received {} points\n".format(self.players[i].name, self.scores[i])
        return msg

    def __str__(self):
        msg = ""
        for i in range(0, self.num_players):
            msg += str(self.players[i]) + "\n"
        return msg

    def next_player_id(self, current_id):
        next_id = int(current_id) + 1
        if next_id == self.num_players:
            next_id = 0
        return next_id

    # Allows get_bids to be called multiple times per hand, state should be saved
    def get_bids(self, dealer_id):
        if self.remaining_bids == self.num_players:
            # No bids yet, initialize info
            self.current_hand.bid = 0
            self.current_hand.bidder = 0
            # Dealer bids last
            self.current_bidder = self.next_player_id(dealer_id)

        # Gather all bids
        for i in range(0, self.remaining_bids):
            bid = self.players[self.current_bidder].declare_bid(self.current_hand, force_two=(self.current_bidder==dealer_id))
            if bid == 1:
                print "Illegal bid of 1, resetting to 0"
                bid = 0
            elif bid > 5:
                print "Illegal bid of > 5 ({}) resetting to 5".format(bid)
                bid = 5
            if self.debug:
                print "BID: {} bid {} and has {}".format(self.players[self.current_bidder].name, bid, " ".join(x.abbrev for x in self.players[self.current_bidder].hand))
            if bid > self.current_hand.bid:
                self.current_hand.bid = bid
                self.current_hand.bidder = self.current_bidder
            self.current_hand.add_bid(self.current_bidder, bid)
            self.current_bidder = self.next_player_id(self.current_bidder)
            self.remaining_bids -= 1

        self.all_bids_are_in = True
        if self.current_hand.bid == 0:
            # No one bid, the dealer takes a two set
            self.forced_two_set = True
        self.current_hand.first_player = self.current_hand.bidder
        if self.debug and not self.forced_two_set:
            print "{} has the highest bid of {}".format(self.players[self.current_hand.bidder].name, self.current_hand.bid)
        if self.debug and self.forced_two_set:
            print "{} was forced to take a two set".format(self.players[dealer_id].name)
        return self.forced_two_set

    def reveal_trump(self):
        self.current_hand.set_trump(self.players[self.current_hand.bidder].get_trump())
        if self.debug:
            print "BID: {} picks {} to be trump".format(self.players[self.current_hand.bidder].name, self.current_hand.trump)

    def update_low_if_needed(self, card, player_id):
        if utils.is_trump(card, self.current_hand.trump) and (self.current_low == None or utils.is_less_than(card, self.current_low, self.current_hand.trump)):
            self.current_low = card
            self.current_low_id = player_id

    def get_hint_from_computer(self, player_id):
        playing_logic = CautiousTaker(debug=self.debug)
        playing_logic.player_id = player_id
        hand = self.players[player_id].hand
        is_bidder = self.current_bidder == player_id
        card_index = playing_logic.choose_card(self.current_hand, self.card_counting_info, hand, self.teams, is_bidder)
        card_to_play = hand[card_index]
        if self.debug:
            print "Computer advises playing {} out of {}".format(str(card_to_play), " ".join(x.abbrev for x in hand))
        return card_to_play


    def get_bid_hint_from_computer(self, player_id, dealer_id):
        bidding_logic = BetterBidding(debug=self.debug)
        hand = self.players[player_id].hand
        bidding_logic.calculate_bid(self.current_hand, hand, force_two=(self.current_bidder==dealer_id))
        bid = bidding_logic.declare_bid()
        trump = bidding_logic.declare_trump()
        if self.debug:
            print "Computer advises bidding {} with {}".format(bid, trump)
        return { "bid": bid, "trump": trump }


    # Allows play_trick to be called multiple times per trick, state should be saved
    def play_trick(self):
        if self.remaining_players == self.num_players:
            # No one has played yet, initialize current_player
            self.current_player = self.current_hand.first_player

        msg = ""
        for i in range(0, self.remaining_players):
            if self.debug:
                # Grab this before playing a card so that card is included
                msg = str(self.players[self.current_player])
            card = self.players[self.current_player].play_card(self.current_hand, self.card_counting_info, self.teams)
            # Because you don't need to take low home to get the point
            self.update_low_if_needed(card, self.current_player)
            if self.debug:
                print "{} plays {}".format(msg, str(card))
            self.current_hand.add_card(self.current_player, card)
            self.card_counting_info.card_was_played(self.current_player, card, self.current_hand.current_trick)
            self.current_player = self.next_player_id(self.current_player)
            self.remaining_players -= 1

        # Give all cards to winner
        cards = self.current_hand.current_trick.get_all_cards_as_stack()
        winner_id = self.current_hand.current_trick.get_winner_id()
        self.players[winner_id].add_cards_to_pile(cards)
        # Tell each player the results of the trick
        for i in range(0, self.num_players):
            self.players[i].save_results_of_trick(winner_id, self.current_hand.get_cards_played())
        # Reset for the next trick
        self.prepare_for_next_trick()
        self.current_hand.first_player = winner_id
        if self.debug:
            print "{} won {}\n".format(self.players[winner_id].name, " ".join(x.abbrev for x in cards))
