# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS
from smear_utils import SmearUtils as utils
from card_counting import CardCounting

rank_values = POKER_RANKS

class SmearPlayingLogic:
    def __init__(self, debug=False):
        self.debug = debug
        self.player_id = None
        self.teams = None

    def choose_card(self, current_hand, card_counting_info, my_hand, teams, is_bidder):
        pass

# TODO: write more and better versions of these
class JustGreedyEnough(SmearPlayingLogic):
    def find_lowest_card_index_to_beat(self, my_hand, card_to_beat, lead_suit, trump):
        lowest_index = None
        if utils.is_trump(card_to_beat, trump):
            # Card to beat is trump, see if I have a higher trump
            my_trump = utils.get_trump_indices(trump, my_hand)
            for idx in my_trump:
                if utils.is_less_than(card_to_beat, my_hand[idx], trump):
                    lowest_index = idx
        elif card_to_beat.suit == lead_suit:
            my_trump = utils.get_trump_indices(trump, my_hand)
            if len(my_trump) != 0:
                # Card to beat isn't trump, but I have trump. Play my lowest trump
                lowest_index = my_trump[0]
            else:
                matching_idxs = my_hand.find(card_to_beat.suit, sort=True, ranks=rank_values)
                for idx in matching_idxs:
                    # Play the lowest card in the matching suit that will beat the card to beat
                    if my_hand[idx].gt(card_to_beat, ranks=rank_values):
                        lowest_index = idx
        else:
            # Card to beat isn't trump and isn't the lead suit, this doesn't make sense
            print "Error: card to beat seems incorrect: {}".format(card_to_beat)
        return lowest_index
        
    def find_strongest_card(self, my_hand, trump):
        my_trump = utils.get_trump_indices(trump, my_hand)
        strongest_idx = None
        if len(my_trump) != 0:
            strongest_idx = my_trump[-1]
        else:
            my_hand.sort(ranks=rank_values)
            strongest_idx = len(my_hand) - 1
        return strongest_idx

    def find_lowest_card_index(self, my_hand, lead_suit, trump):
        lowest_index = None
        lowest_trump_index = None
        # First try following suit.
        my_hand.sort(ranks=rank_values)
        indices = []
        if lead_suit == "Trump":
            indices = utils.get_trump_indices(trump, my_hand)
            indices.reverse()
        else:
            indices = my_hand.find(lead_suit, sort=True, ranks=rank_values)
        if len(indices) == 0:
            indices = range(0, len(my_hand))
        for idx in indices:
            if utils.is_trump(my_hand[idx], trump) and lowest_trump_index == None:
                lowest_trump_index = idx
            else:
                lowest_index = idx
                break
        if lowest_index == None:
            lowest_index = lowest_trump_index
        return lowest_index

    def choose_card(self, current_hand, card_counting_info, my_hand, teams, is_bidder):
        idx = 0
        if len(current_hand.current_trick.cards) == 0:
            # I'm the first player. Choose my strongest card
            idx = self.find_strongest_card(my_hand, current_hand.trump)
        else:
            # Otherwise choose the lowest card to beat the current highest card
            idx = self.find_lowest_card_index_to_beat(my_hand, current_hand.current_trick.current_winning_card, current_hand.current_trick.lead_suit, current_hand.trump)
            if idx == None:
                # If we can't beat it, then just play the lowest card, following suit as needed
                idx = self.find_lowest_card_index(my_hand, current_hand.current_trick.lead_suit, current_hand.trump)

        return idx



class CautiousTaker(SmearPlayingLogic):

    def get_A_K_Q_of_trump(self, my_hand, trump):
        idx = None
        indices = utils.get_trump_indices(trump, my_hand)
        if len(indices) is not 0 and my_hand[indices[-1]].value in "Ace King Queen":
            idx = indices[-1]
        if idx is not None and self.debug:
            print "get_A_K_Q_of_trump chooses {}".format(my_hand[idx])
        return idx


    def get_lowest_trump(self, my_hand, trump):
        idx = None
        indices = utils.get_trump_indices(trump, my_hand)
        if len(indices) is not 0:
            idx = indices[0]
        if idx is not None and self.debug:
            print "get_lowest_trump chooses {}".format(my_hand[idx])
        return idx


    def get_A_K_Q_J_of_off_suit(self, my_hand, trump):
        idx = None
        tmp_hand = pydealer.Stack(cards=my_hand.cards)
        # Sorts lowest to highest
        tmp_hand.sort(ranks=rank_values)
        # Now highest to lowest
        tmp_hand.reverse()
        for card in tmp_hand:
            if utils.is_trump(card, trump):
                # Skip all trump
                continue
            if card.value in "Ace King Queen Jack":
                # If it is a A, K, Q, or J, then find its index in my_hand
                idx = my_hand.find(card.abbrev)[0]
                break
        if idx is not None and self.debug:
            print "get_A_K_Q_J_of_off_suit chooses {}".format(my_hand[idx])
        return idx


    def get_below_10_of_off_suit(self, my_hand, trump):
        idx = None
        tmp_hand = pydealer.Stack(cards=my_hand.cards)
        # Sorts lowest to highest
        tmp_hand.sort(ranks=rank_values)
        for card in tmp_hand:
            if utils.is_trump(card, trump):
                # Skip all trump
                continue
            elif card.value in "Ace King Queen Jack 10":
                # If it is a A, K, Q, J, or 10, skip it
                continue
            else:
                idx = my_hand.find(card.abbrev)[0]
                break
        if idx is not None and self.debug:
            print "get_below_10_of_off_suit chooses {}".format(my_hand[idx])
        return idx


    def get_any_card(self, my_hand):
        # We should only be calling this if we can only play an off-suit 10
        idx = None
        if len(my_hand) > 0:
            idx = 0
        if idx is not None and self.debug:
            print "get_any_card chooses {}".format(my_hand[idx])
        return idx


    def take_jack_or_jick_if_possible(self, my_hand, current_trick, card_counting_info):
        idx = None
        jack_or_jick = False
        jick_found = False
        for card in current_trick.cards:
            if card.value == "Jack" and utils.is_trump(card, current_trick.trump):
                # Jack or Jick found
                jack_or_jick = True
                if card.suit != current_trick.trump:
                    jick_found = True
                break
        if jack_or_jick:
            # First check to see if I can play AKQ
            idx = self.get_A_K_Q_of_trump(my_hand, current_trick.trump)
            if idx is not None:
                if not utils.is_new_card_higher(current_trick.current_winning_card, my_hand[idx], current_trick.trump):
                    idx = None
            if idx is None and jick_found:
                # If no AKQ, check to see if I have a Jack that can safely take the Jick
                indices = utils.get_trump_indices(current_trick.trump, my_hand)
                for index in indices:
                    if my_hand[index].value == "Jack" and my_hand[index].suit == current_trick.trump and card_counting_info.safe_to_play(self.player_id, my_hand[index], current_trick, self.teams):
                        idx = index
                        break
        if idx is not None and self.debug:
            print "take_jack_or_jick_if_possible chooses {}".format(my_hand[idx])
        return idx


    def take_ten_if_possible(self, my_hand, current_trick, card_counting_info):
        idx = None
        ten_card = None
        for card in current_trick.cards:
            if card.value == "10":
                # Ten found
                ten_card = card
                break
        if ten_card is not None:
            indices = utils.get_legal_play_indices(current_trick.lead_suit, current_trick.trump, my_hand)
            # First check to see if I can safely take it with a non-trump
            if idx is None:
                for index in indices:
                    if utils.is_trump(my_hand[index], current_trick.trump):
                        continue
                    if utils.is_new_card_higher(current_trick.current_winning_card, my_hand[index], current_trick.trump) and card_counting_info.safe_to_play(self.player_id, my_hand[index], current_trick, self.teams):
                        idx = index
                        break
            # Then check to see if I can safely take it with a jack or jick
            if idx is None:
                indices = utils.get_trump_indices(current_trick.trump, my_hand)
                for index in indices:
                    if my_hand[index].value == "Jack" and card_counting_info.safe_to_play(self.player_id, my_hand[index], current_trick, self.teams):
                        idx = index
                        break
            # Then check to see if I can take it with a low trump (including 10)
            if idx is None:
                indices = utils.get_trump_indices(current_trick.trump, my_hand)
                for index in indices:
                    if my_hand[index].value not in "Ace King Queen Jack" and utils.is_new_card_higher(current_trick.current_winning_card, my_hand[index], current_trick.trump):
                        idx = index
                        break
            # Then see if there are any jacks or jicks left still, and if not if I can take it with an AKQ
            if idx is None:
                if not card_counting_info.jack_or_jick_still_out():
                    idx = self.get_A_K_Q_of_trump(my_hand, current_trick.trump)
        if idx is not None and self.debug:
            print "take_10_if_possible chooses {}".format(my_hand[idx])
        return idx


    def take_jack_or_jick_if_high_cards_are_out(self, my_hand, current_trick, card_counting_info):
        idx = None
        highest_card = card_counting_info.highest_card_still_out(current_trick.trump, is_trump=True)
        if highest_card == None:
            return None
        indices = utils.get_trump_indices(current_trick.trump, my_hand)
        for index in indices:
            if my_hand[index].value == "Jack" and card_counting_info.safe_to_play(self.player_id, my_hand[index], current_trick, self.teams):
                if my_hand[index].suit == current_trick.trump and highest_card.value in "Ace King Queen":
                    # If I have a Jack, play if there are still A K Q out
                    idx = index
                    break
                elif my_hand[index].suit != current_trick.trump and (highest_card.value in "Ace King Queen" or ( highest_card.value == "Jack" and highest_card.suit == current_trick.trump)):
                    # If I have a Jick, play if there are still A K Q Jack out
                    idx = index
                    break
        if idx is not None and self.debug:
            print "take_jack_or_jick_if_high_cards_are_out chooses {}".format(my_hand[idx])
        return idx


    def take_home_ten_safely(self, my_hand, current_trick, card_counting_info):
        idx = None
        ten_trump = None
        indices = utils.get_legal_play_indices(current_trick.lead_suit, current_trick.trump, my_hand)
        for index in indices:
            if my_hand[index].value == "10" and utils.is_trump(my_hand[index], current_trick.trump):
                # Save for later, try other 10s first
                ten_trump = index
                continue
            if my_hand[index].value == "10" and card_counting_info.safe_to_play(self.player_id, my_hand[index], current_trick, self.teams):
                idx = index
                break
        if idx is None and ten_trump is not None and card_counting_info.safe_to_play(self.player_id, my_hand[ten_trump], current_trick, self.teams):
            idx = ten_trump

        if idx is not None and self.debug:
            print "take_home_ten_safely chooses {}".format(my_hand[idx])
        return idx


    def take_with_off_suit(self, my_hand, current_trick, card_counting_info):
        idx = None
        indices = utils.get_legal_play_indices(current_trick.lead_suit, current_trick.trump, my_hand)
        for index in indices:
            if utils.is_trump(my_hand[index], current_trick.trump):
                # Skip all trump
                continue
            if utils.is_new_card_higher(current_trick.current_winning_card, my_hand[index], current_trick.trump) and card_counting_info.safe_to_play(self.player_id, my_hand[index], current_trick, self.teams):
                # Find the lowest card that can win the trick
                idx = index
                break
        if idx is not None and self.debug:
            print "take_with_off_suit chooses {}".format(my_hand[idx])
        return idx


    def get_lowest_spare_trump_to_lead(self, my_hand, current_trick):
        idx = None
        indices = utils.get_trump_indices(current_trick.trump, my_hand)
        jacks_and_jicks = 0
        for index in indices:
            if my_hand[index].value == "Jack":
                jacks_and_jicks += 1
        non_jacks = len(indices) - jacks_and_jicks

        # If we have a jack or jick, make sure we keep one extra trump to protect it
        if non_jacks > 1:
            for index in indices:
                if my_hand[index].value not in "Ace King Queen Jack 10":
                    idx = index
                    break

        if idx is not None and self.debug:
            print "get_lowest_spare_trump_to_lead chooses {}".format(my_hand[idx])
        return idx


    def take_with_low_trump_if_game_points(self, my_hand, current_trick, card_counting_info):
        idx = None
        indices = utils.get_trump_indices(current_trick.trump, my_hand)
        game_points = utils.calculate_game_score(current_trick.cards)
        # Only take 3 or more game points
        if len(indices) > 1 and game_points > 3:
            for index in indices:
                if my_hand[index].value not in "Ace King Queen Jack 10" and utils.is_new_card_higher(current_trick.current_winning_card, my_hand[index], current_trick.trump):
                    idx = index
                    break
        if idx is not None and self.debug:
            print "take_with_low_trump_if_game_points chooses {}".format(my_hand[idx])
        return idx


    def get_a_loser(self, my_hand, current_trick):
        idx = None
        indices = utils.get_legal_play_indices(current_trick.lead_suit, current_trick.trump, my_hand)
        for index in indices:
            if utils.is_trump(my_hand[index], current_trick.trump):
                continue
            if my_hand[index].value not in "Ace King Queen Jack 10":
                idx = index
                break
        if idx is not None and self.debug:
            print "get_a_loser chooses {}".format(my_hand[idx])
        return idx


    def get_least_valuable_face_card(self, my_hand, current_trick):
        idx = None
        indices = utils.get_legal_play_indices(current_trick.lead_suit, current_trick.trump, my_hand)
        for index in indices:
            if utils.is_trump(my_hand[index], current_trick.trump):
                continue
            if my_hand[index].value not in "10":
                idx = index
                break
        if idx is not None and self.debug:
            print "get_least_valuable_face_card chooses {}".format(my_hand[idx])
        return idx


    def get_least_valuable_trump(self, my_hand, trump):
        idx = None
        indices = utils.get_trump_indices(trump, my_hand)
        for index in indices:
            if my_hand[index].value in "10 Jack":
                # Try to skip 10s and Jacks if we can
                continue
            idx = index
            break
        if idx == None and len(indices) > 0:
            idx = indices[0]
        if idx is not None and self.debug:
            print "get_least_valuable_trump chooses {}".format(my_hand[idx])
        return idx


    def get_the_least_worst_card_to_lose(self, my_hand, current_trick):
        idx = None
        indices = utils.get_legal_play_indices(current_trick.lead_suit, current_trick.trump, my_hand)
        for index in indices:
            if my_hand[index].value == "10":
                # Try to skip 10s if we can
                continue
            idx = index
            break
        if idx == None:
            idx = indices[0]
        if idx is not None and self.debug:
            print "get_the_least_worst_card_to_lose chooses {}".format(my_hand[idx])
        return idx


    def give_teammate_jack_or_jick_if_possible(self, my_hand, current_trick, card_counting_info):
        idx = None
        if self.teams == None or self.teams == []:
            return None
        if card_counting_info.is_teammate_taking_trick(self.player_id, current_trick, self.teams):
            indices = utils.get_trump_indices(current_trick.trump, my_hand)
            for index in indices:
                if my_hand[index].value == "Jack":
                    idx = index
                    break
        if idx is not None and self.debug:
            print "give_teammate_jack_or_jick_if_possible chooses {}".format(my_hand[idx])
        return idx


    def give_teammate_ten_if_possible(self, my_hand, current_trick, card_counting_info):
        idx = None
        if self.teams == None or self.teams == []:
            return None
        if card_counting_info.is_teammate_taking_trick(self.player_id, current_trick, self.teams):
            indices = utils.get_legal_play_indices(current_trick.lead_suit, current_trick.trump, my_hand)
            for index in indices:
                if my_hand[index].value == "10":
                    idx = index
                    break
        if idx is not None and self.debug:
            print "give_teammate_ten_if_possible chooses {}".format(my_hand[idx])
        return idx


    def choose_card(self, current_hand, card_counting_info, my_hand, teams, is_bidder):
        self.teams = teams
        idx = None
        # First player, leading the trick...
        if len(current_hand.current_trick.cards) == 0:
            # Play A, K, Q of trump
            idx = self.get_A_K_Q_of_trump(my_hand, current_hand.trump)
            if idx is None and is_bidder and len(my_hand) == 6:
                # (If bidder and I didn't have AKQ, and this is first trick, play lowest trump)
                idx = self.get_lowest_trump(my_hand, current_hand.trump)
            if idx is None and is_bidder and len(my_hand) == 5:
                # If bidder and this is second trick, and I didn't have AKQ, play another trump if I have one to spare
                idx = self.get_lowest_spare_trump_to_lead(my_hand, current_hand.current_trick)
            # Play A, K, Q, J of other suits
            if idx is None:
                idx = self.get_A_K_Q_J_of_off_suit(my_hand, current_hand.trump)
            # Play low of other suit
            if idx is None:
                idx = self.get_below_10_of_off_suit(my_hand, current_hand.trump)
            # Play lowest trump
            if idx is None:
                idx = self.get_lowest_trump(my_hand, current_hand.trump)
            # Play anything (should be just 10 off suit at this point)
            if idx is None:
                idx = self.get_any_card(my_hand)
        else:
            # Not the first player
            # Give my teammate a jack or jick, if possible
            idx = self.give_teammate_jack_or_jick_if_possible(my_hand, current_hand.current_trick, card_counting_info)
            # If I can take a Jack or Jick, take it
            if idx is None:
                idx = self.take_jack_or_jick_if_possible(my_hand, current_hand.current_trick, card_counting_info)
            # If I can take a 10, take it
            if idx is None:
                idx = self.take_ten_if_possible(my_hand, current_hand.current_trick, card_counting_info)
            # If there are high trump still out but I can safely take home my jack or jick, play it
            if idx is None:
                idx = self.take_jack_or_jick_if_high_cards_are_out(my_hand, current_hand.current_trick, card_counting_info)
            # Give my teammate a 10, if possible
            if idx is None:
                idx = self.give_teammate_ten_if_possible(my_hand, current_hand.current_trick, card_counting_info)
            # If I can safely take home a ten, take it
            if idx is None:
                idx = self.take_home_ten_safely(my_hand, current_hand.current_trick, card_counting_info)
            # If I can take the trick with a non-trump, take it
            if idx is None:
                idx = self.take_with_off_suit(my_hand, current_hand.current_trick, card_counting_info)
            # If there is a face card and I have two or more low trump, take it
            if idx is None:
                idx = self.take_with_low_trump_if_game_points(my_hand, current_hand.current_trick, card_counting_info)
            # Play a loser
            if idx is None:
                idx = self.get_a_loser(my_hand, current_hand.current_trick)
            # Play a face card to save trump and 10s
            if idx is None:
                idx = self.get_least_valuable_face_card(my_hand, current_hand.current_trick)
            # Play lowest trump
            if idx is None:
                idx = self.get_least_valuable_trump(my_hand, current_hand.current_trick.trump)
            # At this point we likely only have 10s left
            if idx == None:
                idx = self.get_the_least_worst_card_to_lose(my_hand, current_hand.current_trick)

        return idx


