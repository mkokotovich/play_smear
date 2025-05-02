import logging

from django.db.models import Q

from apps.smear.cards import Card, Deck
from apps.smear.models import Play

LOG = logging.getLogger(__name__)


def card_has_been_played(hand, card):
    return Play.objects.filter(trick__hand=hand, card=card.representation).exists()


def highest_card_still_out(hand, suit, ignore_card=None):
    all_plays = Play.objects.filter(trick__hand=hand)
    all_cards_played = [Card(representation=play.card) for play in all_plays]
    if ignore_card:
        all_cards_played = [card for card in all_cards_played if card != ignore_card]

    cards_played_from_suit = [card for card in all_cards_played if card.is_suit(suit, hand.trump)]
    cards_played_rep = [card.representation for card in cards_played_from_suit]

    all_cards_from_suit = [card for card in Deck().cards if card.is_suit(suit, hand.trump)]
    all_cards_sorted = sorted(all_cards_from_suit, key=lambda c: c.trump_rank(hand.trump), reverse=True)

    highest_not_played = next((card for card in all_cards_sorted if card.representation not in cards_played_rep), None)

    return highest_not_played


def jack_or_jick_still_out(hand):
    jack_rep = Card(value="jack", suit=hand.trump).representation
    jick_rep = Card(value="jack", suit=Card.jick_suit(hand.trump)).representation
    jboys_played = Play.objects.filter(Q(card=jack_rep) | Q(card=jick_rep), trick__hand=hand).count()
    return jboys_played < 2


def is_teammate_taking_trick(hand, trick, player, plays):
    if hand.game.num_teams == 0:
        return False

    current_winning_play = trick.find_winning_play(plays)
    if current_winning_play.player.team != player.team:
        return False

    # Pretend that we are playing that card, if we would take the trick then
    # our teammate is taking the trick
    return not could_be_defeated(hand, trick, player, Card(representation=current_winning_play.card), plays, already_played=True)


# Returns true if it is known that no one else (besides teammates) in the trick can take this card
def safe_to_play(hand, trick, player, card, plays):
    # Before checking anything, make sure we can beat the current winning card
    # (or the current winning card belongs to a teammate)
    current_winning_play = trick.find_winning_play(plays)
    if not Card(representation=current_winning_play.card).is_less_than(
        card, hand.trump
    ) and not is_teammate_taking_trick(hand, trick, player, plays):
        LOG.debug(f"safe_to_play {card} would be defeated by the current winning play")
        return False

    return not could_be_defeated(hand, trick, player, card, plays)


def could_be_defeated(hand, trick, player, card, plays, already_played=False):
    # Check to see if it is the highest remaining card of that suit
    suit_to_check = hand.trump if card.is_trump(hand.trump) else card.suit
    ignore_card = card if already_played else None
    highest_card_left_of_same_suit = highest_card_still_out(hand, suit_to_check, ignore_card=ignore_card)
    is_highest_left_of_same_suit = card.representation == highest_card_left_of_same_suit.representation

    plays_so_far = len(plays)
    # subtract one to account for me
    remaining_plays = hand.game.num_players - plays_so_far - 1
    current_player = player

    while remaining_plays != 0:
        remaining_plays -= 1
        # next_player is a db query
        # TODO: rework so we don't need players, just IDs
        next_player = hand.game.next_player(current_player)
        current_player = next_player

        if is_highest_left_of_same_suit and card.is_trump(hand.trump):
            LOG.debug(
                f"could_be_defeated {card} breaking because it is highest remaining trump (excluding cards already played this hand)"
            )
            break
        elif hand.game.num_teams != 0 and player.team == next_player.team:
            # This is a teammate
            LOG.debug(f"could_be_defeated {card} continuing because {next_player} is a teammate")
            continue
        elif card.is_trump(hand.trump) or is_highest_left_of_same_suit:
            # If we don't have the highest remaining trump, but we have a trump or
            # the highest card left of its suit, then we need everyone after
            # us to be out of trump
            if str(next_player.id) in hand.players_out_of_suits.get(hand.trump, []):
                LOG.debug(f"could_be_defeated {card} continuing because {next_player} is out of trump")
                continue
        else:
            # If we don't have the highest of the suit and we don't have trump, we need
            # everyone after us to be out of trump and that suit
            if str(next_player.id) in hand.players_out_of_suits.get(hand.trump, []) and str(
                next_player.id
            ) in hand.players_out_of_suits.get(card.suit, []):
                LOG.debug(f"could_be_defeated {card} continuing because {next_player} is out of trump and {card.suit}")
                continue
        # If we made it through the if/else's, that means this player could have cards that can take ours
        LOG.debug(f"could_be_defeated {card} True: A remaining player could take our card")
        return True
    LOG.debug(f"could_be_defeated {card} can not be defeated by any remaining plays")
    return False
