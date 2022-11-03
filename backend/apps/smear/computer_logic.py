import logging

from apps.smear.cards import SUITS, Card
from apps.smear import card_counting


LOG = logging.getLogger(__name__)


def computer_bid(player, hand):
    bid_value, trump_value = calculate_bid(player, hand)

    if hand.high_bid and bid_value <= hand.high_bid.bid:
        LOG.info("Unable to beat current high bid, passing")
        bid_value = 0

    return bid_value, trump_value


def computer_play_card(player, trick):
    card = choose_card(player, trick)

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
    buffer_required = num_expected_remaining_trump * 0.6
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


def get_A_K_Q_of_trump(player, trump):
    my_trump = player.get_trump(trump)
    highest_AKQ = next((card for card in my_trump if card.value in ("ace", "king", "queen")), None)
    if highest_AKQ:
        LOG.debug(f"get_A_K_Q_of_trump chooses {highest_AKQ}")
    return highest_AKQ


def get_lowest_trump(player, trump):
    my_trump = player.get_trump(trump)
    lowest_trump = my_trump[-1] if my_trump else None
    if lowest_trump:
        LOG.debug(f"get_lowest_trump chooses {lowest_trump}")
    return lowest_trump


def get_lowest_spare_trump_to_lead(player, trump):
    my_trump = player.get_trump(trump)
    all_spare_trump = [card for card in my_trump if card.value not in ("ace", "king", "queen", "jack", "10")]
    spare_trump = all_spare_trump[-1] if all_spare_trump else None

    if spare_trump:
        LOG.debug(f"get_lowest_spare_trump_to_lead chooses {spare_trump}")
    return spare_trump


def get_A_K_Q_J_of_off_suit(player, trump):
    my_cards = player.get_cards()
    off_suit_AKQJ = [card for card in my_cards if card.value in ("ace", "king", "queen", "jack") and not card.is_trump(trump)]
    off_suit_AKQJ_sorted = sorted(off_suit_AKQJ, key=lambda c: c.rank(), reverse=True)
    highest_card = off_suit_AKQJ_sorted[0] if off_suit_AKQJ_sorted else None

    if highest_card:
        LOG.debug(f"get_A_K_Q_J_of_off_suit chooses {highest_card}")
    return highest_card


def get_below_10_of_off_suit(player, trump):
    my_cards = player.get_cards()
    off_suit_lows = [card for card in my_cards if card.value not in ("ace", "king", "queen", "jack", "10") and not card.is_trump(trump)]
    off_suit_lows_sorted = sorted(off_suit_lows, key=lambda c: c.rank(), reverse=True)
    highest_card = off_suit_lows_sorted[0] if off_suit_lows_sorted else None

    if highest_card:
        LOG.debug(f"get_below_10_of_off_suit chooses {highest_card}")
    return highest_card


def get_any_card(player, trump):
    # We should only be calling this if we can only play an off-suit 10
    card = player.get_cards()[0]
    if card.value != "10":
        LOG.warning(f"get_any_card chooses {card}, but it shouldn't have to do this")

    LOG.debug(f"get_any_card chooses {card}")
    return card


def give_teammate_jack_or_jick_if_possible(hand, player):
    card = None
    if card_counting.is_teammate_taking_trick(hand, player):
        my_trump = player.get_trump(hand.trump)
        card = next((card for card in my_trump if card.value == "jack"), None)
    if card:
        LOG.debug(f"give_teammate_jack_or_jick_if_possible chooses {card}")
    return card


def take_jack_or_jick_if_possible(hand, player):
    card = None
    cards_played = [Card(representation=play.card) for play in hand.current_trick.plays.all()]
    jboys = [card for card in cards_played if card.is_trump(hand.trump) and card.value == "jack"]
    only_jick = len(jboys) == 1 and jboys[0].is_jick(hand.trump)

    current_winning_play = hand.current_trick.find_winning_play()
    current_winning_card = Card(representation=current_winning_play.card)

    if jboys:
        # First check to see if I can play AKQ
        card = get_A_K_Q_of_trump(player, hand.trump)
        if card and not current_winning_card.is_less_than(card, hand.trump):
            # If our AKQ can't beat the current winning card, don't select it
            card = None
        elif not card and only_jick:
            # If no AKQ, check to see if I have a Jack that can safely take the Jick
            my_trump = player.get_trump(hand.trump)
            jack = next((card for card in my_trump if card.value == "jack"), None)
            if jack and card_counting.safe_to_play(hand, player, jack):
                card = jack
    if card:
        LOG.debug("take_jack_or_jick_if_possible chooses {card}")
    return card


def take_jack_or_jick_if_high_cards_are_out(hand, player):
    card = None
    highest_trump = card_counting.highest_card_still_out(hand, hand.trump)
    if not highest_trump or highest_trump.value not in ("ace", "king", "queen", "jack"):
        return None
    jboys = [card for card in player.get_trump(hand.trump) if card.value == "jack"]
    for jboy in jboys:
        if card_counting.safe_to_play(hand, player, jboy):
            if jboy.is_jack() and highest_trump.value in ("ace", "king", "queen"):
                # If I have a Jack, play if there are still A K Q out
                card = jboy
                break
            elif jboy.is_jick() and (highest_trump.value in ("ace", "king", "queen") or highest_trump.is_jack()):
                # If I have a Jick, play if there are still A K Q Jack out
                card = jboy
                break
    if card:
        LOG.debug(f"take_jack_or_jick_if_high_cards_are_out chooses {card}")
    return card


def take_ten_if_possible(hand, player):
    card = None
    ten_card = None
    cards_played = [Card(representation=play.card) for play in hand.current_trick.plays.all()]
    ten_card = next((card for card in cards_played if card.value == "10"), None)

    if ten_card:
        if card_counting.is_teammate_taking_trick(hand, player):
            return None

        legal_plays = [card for card in player.get_cards() if not hand.current_trick.is_card_invalid_to_play(card, player)]
        # Sorted from least to most
        legal_trump = sorted([card for card in legal_plays if card.is_trump(hand.trump)], key=lambda c: c.trump_rank(hand.trump))
        legal_offsuit = sorted([card for card in legal_plays if not card.is_trump(hand.trump)], key=lambda c: c.rank())

        current_winning_play = hand.current_trick.find_winning_play()
        current_winning_card = Card(representation=current_winning_play.card)

        # First check to see if I can safely take it with a non-trump
        for taker in legal_offsuit:
            if current_winning_card.is_less_than(taker, hand.trump) and card_counting.safe_to_play(hand, player, taker):
                card = taker
                break
        # Then check to see if I can safely take it with a jack or jick or 10
        if not card:
            for taker in legal_trump:
                if (taker.value == "jack" or taker.value == "10") and card_counting.safe_to_play(hand, player, taker):
                    card = taker
                    break
        # Then check to see if I can take it with a low trump
        if not card:
            for taker in legal_trump:
                if taker.value not in ("ace", "king", "queen", "jack", "10") and current_winning_card.is_less_than(taker, hand.trump):
                    card = taker
                    break
        # Then see if there are any jacks/jicks left still, and if not if I can take it with an AKQ
        if not card:
            if not card_counting.jack_or_jick_still_out(hand):
                card = get_A_K_Q_of_trump(player, hand.trump)

    if card:
        LOG.debug(f"take_10_if_possible chooses {card}")
    return card


def give_teammate_ten_if_possible(hand, player):
    card = None
    if card_counting.is_teammate_taking_trick(hand, player):
        legal_10s = [card for card in player.get_cards() if card.value == "10" and not hand.current_trick.is_card_invalid_to_play(card, player)]
        non_trump_10 = next((card for card in legal_10s if not card.is_trump(hand.trump)), None)
        if non_trump_10:
            card = non_trump_10
        else:
            card = legal_10s[0] if legal_10s else None

    if card:
        LOG.debug(f"give_teammate_ten_if_possible chooses {card}")
    return card


def take_home_ten_safely(hand, player):
    card = None
    ten_card = None
    legal_10s = [card for card in player.get_cards() if card.value == "10" and not hand.current_trick.is_card_invalid_to_play(card, player)]
    non_trump_10 = next((card for card in legal_10s if not card.is_trump(hand.trump)), None)
    if non_trump_10:
        ten_card = non_trump_10
    else:
        ten_card = legal_10s[0] if legal_10s else None

    if ten_card and card_counting.safe_to_play(hand, player, ten_card):
        card = ten_trump

    if card:
        LOG.debug(f"take_home_ten_safely chooses {card}")
    return card


def take_with_off_suit(hand, player):
    card = None
    if card_counting.is_teammate_taking_trick(hand, player):
        return None

    # smallest to largest
    legal_offsuit = sorted(
        [card for card in player.get_cards() if not card.is_trump(hand.trump) and not hand.current_trick.is_card_invalid_to_play(card, player)],
        key=lambda c: c.rank()
    )
    current_winning_play = hand.current_trick.find_winning_play()
    current_winning_card = Card(representation=current_winning_play.card)

    for taker in legal_offsuit:
        if current_winning_card.is_less_than(taker, hand.trump) and card_counting.safe_to_play(hand, player, taker):
            card = taker
            break
    if card:
        LOG.debug(f"take_with_off_suit chooses {card}")
    return card


def take_with_low_trump_if_game_points(hand, player):
    card = None
    my_trump = player.get_trump(hand.trump, smallest_to_largest=True)
    small_trump = [card for card in my_trump if card.value not in ("ace", "king", "queen", "jack", "10")]
    if len(small_trump) < 2:
        return None

    cards_played = [Card(representation=play.card) for play in hand.current_trick.plays.all()]
    game_points = sum(card.game_points for card in cards_played)
    # Only take 2 or more game points
    if game_points < 2:
        return None

    current_winning_play = hand.current_trick.find_winning_play()
    current_winning_card = Card(representation=current_winning_play.card)
    for taker in small_trump:
        if current_winning_card.is_less_than(taker, hand.trump):
            card = taker
            break
    if card:
        LOG.debug(f"take_with_low_trump_if_game_points chooses {card}")
    return card


def choose_card(player, trick):
    is_bidder = trick.hand.dealer_id == player.id
    trump = trick.hand.trump
    # First player, leading the trick...
    if trick.get_lead_play() is None:
        # Play A, K, Q of trump
        card = get_A_K_Q_of_trump(player, trump)
        if not card and is_bidder and len(player.cards_in_hand) == 6:
            # If bidder and I didn't have AKQ, and this is first trick, play lowest trump
            card = get_lowest_trump(player, trump)
        if not card and is_bidder and len(player.cards_in_hand) == 5:
            # If bidder and this is second trick, and I didn't have AKQ, play another trump if I have one to spare
            card = get_lowest_spare_trump_to_lead(player, trump)
        # Play A, K, Q, J of other suits
        if not card:
            card = get_A_K_Q_J_of_off_suit(player, trump)
        # Play low of other suit
        if not card:
            card = get_below_10_of_off_suit(player, trump)
        # Play lowest trump
        if not card:
            card = get_lowest_trump(player, trump)
        # Play anything (should be just 10 off suit at this point)
        if not card:
            card = get_any_card(player, trump)
    else:
        # Not the first player
        # Give my teammate a jack or jick, if possible
        card = give_teammate_jack_or_jick_if_possible(trick.hand, player)
        # If I can take a Jack or Jick, take it
        if not card:
            card = take_jack_or_jick_if_possible(trick.hand, player)
        # If there are high trump still out but I can safely take home my jack or jick, play it
        if not card:
            card = take_jack_or_jick_if_high_cards_are_out(trick.hand, player)
        # If I can take a 10, take it
        if not card:
            card = take_ten_if_possible(trick.hand, player)
        # Give my teammate a 10, if possible
        if not card:
            card = give_teammate_ten_if_possible(trick.hand, player)
        # If I can safely take home a ten, take it
        if not card:
            card = take_home_ten_safely(trick.hand, player)
        # If I can take the trick with a non-trump, take it
        if not card:
            card = take_with_off_suit(trick.hand, player)
        # If there is a face card and I have two or more low trump, take it
        if not card:
            card = take_with_low_trump_if_game_points(trick.hand, player)

        # TODO start here
        if not card:
            card = next((card for card in player.get_cards() if not trick.is_card_invalid_to_play(card, player)), None)
            LOG.debug(f"TODO not implemented chooses {card}")

        """
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
        """

    return card

# TODO: Rework all of this to fit our new game format
"""


class CautiousTaker(SmearPlayingLogic):



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
