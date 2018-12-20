# Simulator for the card game smear

import pydealer
from pydealer.const import POKER_RANKS

jack_hearts = pydealer.Card(value="Jack", suit="Hearts")
jack_spades = pydealer.Card(value="Jack", suit="Spades")
jack_diamonds = pydealer.Card(value="Jack", suit="Diamonds")
jack_clubs = pydealer.Card(value="Jack", suit="Clubs")
jick_of = {}
jick_of["Hearts"] = jack_diamonds
jick_of["Spades"] = jack_clubs
jick_of["Diamonds"] = jack_hearts
jick_of["Clubs"] = jack_spades

class SmearUtils():


    # Returns the value of card_lhs < card_rhs, following the rules of trump
    @staticmethod
    def is_less_than(card_lhs, card_rhs, trump):
        less_than = False
        if card_lhs == None:
            less_than = True
        elif card_rhs == None:
            less_than = False
        elif SmearUtils.is_trump(card_lhs, trump) and not SmearUtils.is_trump(card_rhs, trump):
            # lhs is trump and rhs isn't, return false
            less_than = False
        elif not SmearUtils.is_trump(card_lhs, trump) and SmearUtils.is_trump(card_rhs, trump):
            # lhs is not trump and rhs is, return true
            less_than = True
        elif SmearUtils.is_trump(card_lhs, trump):
            # Both are trump
            if card_lhs.suit == card_rhs.suit:
                # Neither are Jicks, just compare
                less_than = POKER_RANKS["values"][card_lhs.value] < POKER_RANKS["values"][card_rhs.value]
            else:
                # One of the cards is the jick
                if card_lhs.suit != trump:
                    # card_lhs is a jick, lhs is less than rhs if rhs is greater than or equal to a jack
                    less_than = POKER_RANKS["values"][card_rhs.value] >= POKER_RANKS["values"]["Jack"]
                else:
                    # card_rhs is a jick, lhs is less than rhs if lhs is less than or equal to a 10
                    less_than = POKER_RANKS["values"][card_lhs.value] <= POKER_RANKS["values"]["10"]
        else:
            # Neither are trump, just compare values (although this isn't how tricks are taken)
            print "Warning, comparing cards with different suits"
            less_than = POKER_RANKS["values"][card_lhs.value] < POKER_RANKS["values"][card_rhs.value]
        return less_than


    @staticmethod
    def is_trump(card, trump):
        card_is_trump = False
        if card.suit == trump:
            return True
        elif trump == "Spades":
            return jack_clubs == card
        elif trump == "Clubs":
            return jack_spades == card
        elif trump == "Hearts":
            return jack_diamonds == card
        elif trump == "Diamonds":
            return jack_hearts == card
        return card_is_trump


    @staticmethod
    def is_new_card_higher(current_winning_card, new_card, trump, debug=False):
        is_higher = False
        if SmearUtils.is_trump(current_winning_card, trump) or SmearUtils.is_trump(new_card, trump):
            # At least one of the cards is trump, compare to new card
            is_higher = not SmearUtils.is_less_than(new_card, current_winning_card, trump)
            if debug:
                print "At least one card is trump, {} is higher than {}".format(str(new_card) if is_higher else str(current_winning_card), str(current_winning_card) if is_higher else str(new_card))
        elif new_card.suit == current_winning_card.suit:
            # Both are not trump, but are the same suit
            is_higher = POKER_RANKS["values"][new_card.value] > POKER_RANKS["values"][current_winning_card.value]
            if debug:
                print "Suit is same ({}), {} is higher than {}".format(new_card.suit, str(new_card) if is_higher else str(current_winning_card), str(current_winning_card) if is_higher else str(new_card))
        else:
            # new_card is a different suit, and not trump, so is not higher
            is_higher = False
            if debug:
                print "Suit is different, {} was unable to follow suit".format(str(new_card))

        return is_higher


    @staticmethod
    def insert_card_into_sorted_index_list(indices, stack, card_index):
        # Assumes sorted from smallest to largest
        inserted = False
        for i in range(0, len(indices)):
            # Loop through indices, comparing card in stack at that index to
            # card in stack at card_index
            if stack[indices[i]].lt(stack[card_index], ranks=POKER_RANKS):
                # New card is larger, keep going
                continue
            else:
                # New card is smaller, insert here
                indices.insert(i, card_index)
                inserted = True;
                break
        if not inserted:
            # Card is larger than all members, need to insert at end
            indices.append(card_index)


    @staticmethod
    def merge_two_sorted_index_lists(left_indices, right_indices, stack):
        return sorted(left_indices + right_indices, key=lambda x: POKER_RANKS["values"][stack[x].value])


    # Sorted from smallest to largest
    @staticmethod
    def get_legal_play_indices(lead_suit, trump, stack):
        # Find trump indices
        trump_indices = SmearUtils.get_trump_indices(trump, stack)
        if lead_suit == "Trump":
            if len(trump_indices) == 0:
                # No trump and trump was lead, can play anything
                return range(0, len(stack))
            return trump_indices

        # Find indices from the lead suit
        lead_suit_indices = stack.find(lead_suit, sort=True, ranks=POKER_RANKS)

        # Remove the jick, as it is trump, not part of it's usual suit
        jick = jick_of[trump]
        for index in lead_suit_indices:
            if stack[index] == jick:
                lead_suit_indices.remove(index)

        if len(lead_suit_indices) == 0:
            # No lead suit, can play anything
            return range(0, len(stack))

        return SmearUtils.merge_two_sorted_index_lists(lead_suit_indices, trump_indices, stack)


    # Sorted from smallest to largest
    @staticmethod
    def get_trump_indices(trump, stack):
        trump_indices = stack.find(trump, sort=True, ranks=POKER_RANKS)
        jick = jick_of[trump]
        if jick in stack.cards:
            SmearUtils.insert_card_into_sorted_index_list(trump_indices, stack, stack.find(jick.abbrev)[0])
        return trump_indices


    @staticmethod
    def calculate_game_score(cards):
        game_score = 0
        for card in cards:
            if card.value == "10":
                game_score += 10
            if card.value == "Ace":
                game_score += 4
            elif card.value == "King":
                game_score += 3
            elif card.value == "Queen":
                game_score += 2
            elif card.value == "Jack":
                game_score += 1
        return game_score


    # Returns true if other_player is on same team as player_id
    @staticmethod
    def is_on_same_team(player_id, other_player, teams):
        for team in teams:
            if player_id in team:
                return other_player in team
            elif other_player in team:
                return player_id in team
        return False


    # Returns list of teammates
    @staticmethod
    def my_team(player_id, teams):
        for team in teams:
            if player_id in team:
                return team
        return []

