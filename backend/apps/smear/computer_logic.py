import logging

from apps.smear.cards import SUITS


LOG = logging.getLogger(__name__)


def computer_bid(player, hand):
    bid_value, trump_value = calculate_bid(player, hand)

    return bid_value, trump_value


def computer_play_card(player, trick):
    # TODO: playing logic
    card = next((card for card in player.get_cards() if not trick.is_card_invalid_to_play(card, player)), None)
    assert card is not None, f'unable to find a card for {player}, {player.cards_in_hand} are all invalid'

    return card


def calculate_bid(player, hand, aggression_factor=0.2):
    bid = 0
    bid_trump = None

    LOG.debug(f"calculating bid for player {player} with hand {hand}")
    for suit in SUITS:
        tmp_bid = 0
        tmp_bid += expected_points_from_high(player, hand, suit)
        tmp_bid += expected_points_from_low(player, hand, suit)
        tmp_bid += expected_points_from_game(player, hand, suit)
        tmp_bid += expected_points_from_jack_and_jick(player, hand, suit)

        LOG.debug(f"{player} suit {suit} would result in bid of {tmp_bid}")
        if tmp_bid > bid:
            bid, bid_trump = tmp_bid, suit

    # Determine whether to round up or down
    round_up_or_down = 0
    fractional_part = bid - int(bid)
    round_up_or_down = 1 if aggression_factor + fractional_part >= 1 else 0
    # int() always rounds down
    rounded_bid = int(bid) + round_up_or_down

    is_dealer = player.id == hand.dealer_id
    if rounded_bid < 2:
        if not hand.high_bid and is_dealer and rounded_bid == 1:
            # Go for it, otherwise we get set
            LOG.debug("Forced to bid two in order to avoid an automatic set")
            rounded_bid = 2
        else:
            rounded_bid = 0

    return rounded_bid, bid_trump


def choose(n, k):
    """
    A fast way to calculate binomial coefficients by Andrew Dalke (contrib).
    """
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in range(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0


def calculate_percent_that_no_one_else_was_dealt_a_card(cards_per_hand, num_players, possible_cards):
    # subtract cards_per_hand to account for the cards in my hand
    remaining_cards_in_deck = 52 - cards_per_hand
    percent_that_no_one_else_was_dealt_a_card = 1.0

    # percent_that_no_one_else_was_dealt_a_card = (
    #   percent_that_player1_was_not_dealt_a_card *
    #   percent_that_player2_was_not_dealt_a_card *
    #   percent_that_player3_was_not_dealt_a_card *
    #   ...
    # )
    for i in range(0, num_players - 1):
        if (remaining_cards_in_deck - possible_cards) < cards_per_hand:
            percent_that_no_one_else_was_dealt_a_card = 0
            break
        percent_that_no_one_else_was_dealt_a_card *= (
            choose(remaining_cards_in_deck - possible_cards, cards_per_hand) / float(choose(remaining_cards_in_deck, cards_per_hand))
        )
        remaining_cards_in_deck -= cards_per_hand

    return percent_that_no_one_else_was_dealt_a_card


def expected_points_from_high(player, hand, suit):
    exp_points = 0

    cards = player.get_trump(suit)
    if not cards:
        return 0

    # (14 - high_rank) because there are 14 trumps
    high_rank = cards[0].trump_rank(suit)
    other_possible_highs = 14 - high_rank

    percent_that_no_one_else_has_high = calculate_percent_that_no_one_else_was_dealt_a_card(
        len(player.cards_in_hand),
        hand.game.num_players,
        other_possible_highs,
    )

    exp_points = 1 * percent_that_no_one_else_has_high
    if exp_points < 0.3:
        exp_points = 0
    LOG.debug(f"{player} calculates {exp_points:.2f} expected points from high for {suit}")

    return exp_points


def expected_points_from_low(player, hand, suit):
    exp_points = 0

    cards = player.get_trump(suit)
    if not cards:
        return 0

    # (low_rank - 1) because the lowest is 2
    low_rank = cards[-1].trump_rank(suit)
    other_possible_lows = low_rank - 1

    percent_that_no_one_else_has_low = calculate_percent_that_no_one_else_was_dealt_a_card(
        len(player.cards_in_hand),
        hand.game.num_players,
        other_possible_lows,
    )

    exp_points = 1 * percent_that_no_one_else_has_low
    if exp_points < 0.3:
        exp_points = 0
    LOG.debug(f"{player} calculates {exp_points:.2f} expected points from low for {suit}")

    return exp_points


def expected_points_from_game(player, hand, suit):
    exp_points = 0.0

    my_trump = player.get_trump(suit)
    my_cards = player.get_cards()

    for card in my_cards:
        if card.is_trump(suit) and card.value == "10":
            # 10 of trump is valuable, especially if you have many trump
            if len(my_trump) > 2:
                exp_points += 0.6
            else:
                exp_points += 0.3
        elif card.is_trump(suit):
            # All trump cards will help some
            exp_points += 0.1 if card.trump_rank(suit) < 5 else 0.2
        elif card.value in ("ace", "king"):
            # High face cards are worth some
            exp_points += 0.20
        elif card.value in ("queen", "jack"):
            # lower face cards are worth a little less
            exp_points += 0.15

    if exp_points > 1:
        exp_points = 1
    elif exp_points < 0.3:
        exp_points = 0
    LOG.debug(f"{player} calculates {exp_points:.2f} expected points from game for {suit}")

    return exp_points


def expected_total_trump(num_players):
    return {
        2: 3.5,
        3: 5,
        4: 6.5,
        5: 8,
        6: 9.5,
        7: 11,
        8: 12.5,
    }.get(num_players, 0)


def expected_points_from_jack_and_jick(player, hand, suit):
    exp_points = 0
    exp_my_points = 0
    exp_taken_points = 0

    my_trump = player.get_trump(suit)
    num_jacks_and_jicks = len([card for card in my_trump if card.value == "jack"])
    num_non_jacks = len(my_trump) - num_jacks_and_jicks
    num_my_AKQ = len([card for card in my_trump if card.value in ("ace", "king", "queen")])
    num_expected_trump = expected_total_trump(hand.game.num_players)
    num_expected_remaining_trump = num_expected_trump - len(my_trump)
    buffer_required = num_expected_remaining_trump  * 0.6
    expected_jacks_and_jicks = 2 * (6 * hand.game.num_players) / 52

    if num_jacks_and_jicks:
        # How many points will I get from my own Jacks and Jicks
        percentage_someone_takes = (3 - num_my_AKQ) / 3 * (buffer_required - num_non_jacks) / buffer_required
        percentage_someone_takes = 0 if percentage_someone_takes < 0 else percentage_someone_takes

        exp_my_points = num_jacks_and_jicks * (1 - percentage_someone_takes)

    if num_my_AKQ and num_jacks_and_jicks < 2:
        # How many points will I get from taking other Jacks and Jicks
        available_jacks_and_jicks = expected_jacks_and_jicks - num_jacks_and_jicks
        available_jacks_and_jicks = 0 if available_jacks_and_jicks < 0 else available_jacks_and_jicks
        take_factor = 0
        if num_my_AKQ == 1:
            take_factor = 0.1
        elif num_my_AKQ == 2:
            take_factor = 0.75
        elif num_my_AKQ == 3:
            take_factor = 1

        exp_taken_points = available_jacks_and_jicks * take_factor

    exp_points = exp_my_points + exp_taken_points
    LOG.debug(f"{player} calculates {exp_points:.2f} expected points ({exp_my_points:.2f} + {exp_taken_points:.2f}) from jacks_and_jicks for {suit}")
    return exp_points


# TODO: Rework all of this to fit our new game format
"""


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
            # If there are high trump still out but I can safely take home my jack or jick, play it
            if idx is None:
                idx = self.take_jack_or_jick_if_high_cards_are_out(my_hand, current_hand.current_trick, card_counting_info)
            # If I can take a 10, take it
            if idx is None:
                idx = self.take_ten_if_possible(my_hand, current_hand.current_trick, card_counting_info)
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

"""
