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


def is_teammate_taking_trick(hand, player):
    if hand.game.num_teams == 0:
        return False

    current_winning_play = hand.current_trick.find_winning_play()
    if current_winning_play.player.team != player.team:
        return False

    # Pretend that we are playing that card, if we would take the trick then
    # our teammate is taking the trick
    return not could_be_defeated(hand, player, Card(representation=current_winning_play.card), already_played=True)


def update_if_out_of_cards(hand, player, card_played):
    all_plays = Play.objects.filter(trick__hand=hand)
    all_cards_played = [Card(representation=play.card) for play in all_plays]

    suit_played = hand.trump if card_played.is_trump(hand.trump) else card_played.suit
    if card_played.is_trump(hand.trump):
        if len(card for card in all_cards_played if card.is_trump(hand.trump)) == 14:
            # If all trump have been played, everyone is out
            hand.players_out_of_suits[suit_played] = [str(p.id) for p in hand.game.players.all()]
    else:
        # Only 12 cards exist in the jick suit (jick counts as trump)
        expected_cards = 12 if suit_played == Card.jick_suit(hand.trump) else 13
        if len(card for card in all_cards_played if not card.is_trump(hand.trump) and card.suit == suit_played) == expected_cards:
            # If all cards of this suit have been played, everyone is out
            hand.players_out_of_suits[suit_played] = [str(p.id) for p in hand.game.players.all()]

    # Update if the player is out of the suit
    lead_card = Card(representation=hand.current_trick.get_lead_play().card)
    player_is_out = None
    if lead_card.is_trump(hand.trump):
        if not card_played.is_trump(hand.trump):
            player_is_out = hand.trump
    else:
        if not card_played.is_trump(hand.trump) and card_played.suit != lead_card.suit:
            # If player is trumping in, can't tell if he/she is out of lead_suit
            # So if it isn't trump, and isn't the lead_suit, must be out of lead_suit
            player_is_out = lead_card.suit
    existing_outs = hand.players_out_of_suites.get(suit_played, [])
    new_outs = existing_outs if str(player.id) in existing_outs else [*existing_outs, str(player.id)]
    hand.players_out_of_suites[player_is_out] = new_outs


# Returns true if it is known that no one else (besides teammates) in the trick can take this card
def safe_to_play(hand, player, card):
    # Before checking anything, make sure we can beat the current winning card
    # (or the current winning card belongs to a teammate)
    current_winning_play = hand.current_trick.find_winning_play()
    if not Card(representation=current_winning_play.card).is_less_than(card, hand.trump) and not is_teammate_taking_trick(hand, player):
        LOG.debug(f"safe_to_play {card} would be defeated by the current winning play")
        return False

    return not could_be_defeated(hand, player, card)


def could_be_defeated(hand, player, card, already_played=False):
    # Check to see if it is the highest remaining card of that suit
    suit_to_check = hand.trump if card.is_trump(hand.trump) else card.suit
    ignore_card = card if already_played else None
    highest_card_left_of_same_suit = highest_card_still_out(hand, suit_to_check, ignore_card=ignore_card)
    is_highest_left_of_same_suit = card.representation == highest_card_left_of_same_suit.representation

    plays_so_far = hand.current_trick.plays.count()
    # subtract one to account for me
    remaining_plays = hand.game.num_players - plays_so_far - 1
    current_player = player

    while remaining_plays != 0:
        remaining_plays -= 1
        next_player = hand.game.next_player(current_player)
        current_player = next_player

        if is_highest_left_of_same_suit and card.is_trump(hand.trump):
            LOG.debug(f"could_be_defeated {card} breaking because it is highest remaining trump (excluding cards already played this hand)")
            break
        elif player.team == next_player.team:
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
            if str(next_player.id) in hand.players_out_of_suits.get(hand.trump, []) and str(next_player.id) in hand.players_out_of_suits.get(card.suit, []):
                LOG.debug(f"could_be_defeated {card} continuing because {next_player} is out of trump and {card.suit}")
                continue
        # If we made it through the if/else's, that means this player could have cards that can take ours
        LOG.debug(f"could_be_defeated {card} True: A remaining player could take our card")
        return True
    LOG.debug(f"could_be_defeated {card} can not be defeated by any remaining plays")
    return False
